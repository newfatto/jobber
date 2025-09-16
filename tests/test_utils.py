from typing import Any, Dict, List, Tuple
from unittest.mock import patch

import pytest
from psycopg2 import errors

from src.utils import create_db_and_tables, load_data_to_bd


class FakeCursor:
    """Простой курсор: копит вызовы execute и умеет сработать с ошибкой DROP DATABASE."""

    def __init__(self, raise_on_drop: bool = False) -> None:
        self.raise_on_drop = raise_on_drop
        self.executed: List[Tuple[str, Tuple[Any, ...] | None]] = []

    # контекст-менеджер
    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *exc: object) -> None:  # noqa: D401 - стандартный протокол
        ...

    def execute(self, sql: object, params: Tuple[Any, ...] | None = None) -> None:
        sql_text = str(sql)
        if self.raise_on_drop and "DROP DATABASE" in sql_text.upper():
            from psycopg2 import errors
            raise errors.InvalidCatalogName()
        self.executed.append((sql_text, params))


class FakeConn:
    """Минимальная заглушка соединения для psycopg2.connect."""

    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor
        self.commits: int = 0
        self.isolation_level_set: bool = False
        self.closed: bool = False

    # контекст-менеджер
    def __enter__(self) -> "FakeConn":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def cursor(self) -> FakeCursor:
        return self._cursor

    def set_isolation_level(self, *a: Any, **kw: Any) -> None:
        self.isolation_level_set = True

    def commit(self) -> None:
        self.commits += 1

    def close(self) -> None:
        self.closed = True


def make_connect_factory(
    admin_cursor: FakeCursor, work_cursor: FakeCursor
):
    """Функция-«фабрика» для monkeypatch: возвращает нужное соединение по имени БД."""

    def _connect(*, database: str, **_: Any) -> FakeConn:
        # первая фаза: подключение к 'postgres' для создания/удаления БД
        if database == "postgres":
            return FakeConn(admin_cursor)
        # вторая фаза: подключение к целевой БД для создания таблиц/insert'ов
        return FakeConn(work_cursor)

    return _connect



def test_create_db_and_tables_happy_path(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Успешный сценарий: выполняется DROP DATABASE, CREATE DATABASE,
    затем создаются обе таблицы. Проверяем, что печатаются ожидаемые сообщения.
    """
    admin_cur = FakeCursor()          # без ошибок на DROP
    work_cur = FakeCursor()
    monkeypatch.setattr(
        "src.utils.psycopg2.connect",
        make_connect_factory(admin_cur, work_cur),
    )

    create_db_and_tables("mydb", {"host": "h"})  # параметры коннекта не важны

    out = capsys.readouterr().out
    assert 'Создана база данных "mydb"' in out
    assert "Созданы столбцы в таблицах" in out

    # проверяем, что были 2 CREATE TABLE
    create_table_statements = [sql for sql, _ in work_cur.executed if "CREATE TABLE" in sql.upper()]
    assert len(create_table_statements) == 2


def test_create_db_and_tables_no_db_to_drop(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Если БД нет — курсор бросает errors.InvalidCatalogName на DROP DATABASE,
    а функция должна просто вывести предупреждение и продолжить создание.
    """
    admin_cur = FakeCursor(raise_on_drop=True)   # бросаем InvalidCatalogName на DROP
    work_cur = FakeCursor()
    monkeypatch.setattr(
        "src.utils.psycopg2.connect",
        make_connect_factory(admin_cur, work_cur),
    )

    create_db_and_tables("newdb", {"host": "h"})

    out = capsys.readouterr().out
    assert "не существует, пропускаем удаление" in out
    # убеждаемся, что после этого всё равно создавали таблицы
    assert any("CREATE TABLE" in sql.upper() for sql, _ in work_cur.executed)


def test_load_data_to_bd_inserts(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Загружаем по одному работодателю и вакансии: проверяем два INSERT и commit.
    """
    work_cur = FakeCursor()
    conn = FakeConn(work_cur)

    # для load_data_to_bd вызывается только соединение к рабочей БД
    monkeypatch.setattr("src.utils.psycopg2.connect", lambda **_: conn)

    data: Dict[str, List[Dict[str, Any]]] = {
        "employers": [
            {
                "id": "111",
                "name": "TestCo",
                "site_url": "https://t.co",
                "area": {"name": "Moscow"},
                "open_vacancies": 10,
            }
        ],
        "vacancies": [
            {
                "name": "Python Dev",
                "employer": {"id": "111"},
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "area": {"name": "Moscow"},
                "alternate_url": "https://hh.example/v",
            }
        ],
    }

    load_data_to_bd("mydb", data, {"host": "h"})

    # первый INSERT — в employers, второй — в vacancies
    inserts = [sql for sql, _ in work_cur.executed if sql.strip().upper().startswith("INSERT INTO")]
    assert len(inserts) == 2
    assert conn.commits == 1
