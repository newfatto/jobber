import pytest
from src.DBManager import DBManager

@pytest.fixture
def dbm(monkeypatch):
    """Фикстура: DBManager с подменённым connect."""
    db = DBManager("testdb", {})
    class FakeCursor:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def execute(self, *a, **kw): pass
        def fetchall(self): return [("Vacancy", 100000)]
    class FakeConn:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def cursor(self): return FakeCursor()
    monkeypatch.setattr(db, "connect", lambda: FakeConn())
    return db

def test_get_avg_salary(dbm):
    """Метод возвращает список с кортежами (вакансия, число)."""
    rows = dbm.get_avg_salary()
    assert rows == [("Vacancy", 100000)]
