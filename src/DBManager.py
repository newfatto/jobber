from typing import Any, Dict, List, Optional, Tuple, cast

import psycopg2
from psycopg2.extensions import connection as PGConnection


class DBManager:
    """Класс для выполнения запросов к БД."""

    def __init__(self, database_name: str, params: Dict[str, Any]) -> None:
        self.db: str = database_name
        self.params: Dict[str, Any] = params

    def connect(self) -> PGConnection:
        """Создаёт соединение с БД (закрывается контекстным менеджером в методах)."""
        return psycopg2.connect(database=self.db, **self.params)

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Список всех компаний и количество вакансий у каждой.
        Returns: [(employer_name, vacancies_count), ...]
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                SELECT e.name AS employer_name, COUNT(v.vacancy_id) AS vacancies_count
                FROM employers AS e
                LEFT JOIN vacancies AS v USING(employer_id)
                GROUP BY e.name
                ORDER BY vacancies_count DESC
                """
                )
                rows = cast(List[Tuple[str, int]], cur.fetchall())
                return rows

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], str]]:
        """
        Список всех вакансий с полями: vacancy_name, employer_name, salary_from, url.
        salary_from может быть NULL => Optional[int].
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT v.name, e.name, v.salary_from, v.url
                FROM vacancies AS v
                JOIN employers AS e
                USING(employer_id)"""
                )
                rows = cast(List[Tuple[str, str, Optional[int], str]], cur.fetchall())
                return rows

    def get_avg_salary(self) -> List[Tuple[str, float]]:
        """
        Средняя зарплата по вакансиям, где salary_from указан.
        Возвращает: [(vacancy_name, avg_salary), ...]
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT v.name, AVG(salary_from) AS avg_salary
                FROM vacancies AS v
                WHERE salary_from IS NOT NULL
                GROUP BY v.name
                ORDER BY avg_salary DESC"""
                )
                rows = cast(List[Tuple[str, int]], cur.fetchall())
                return rows

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, float]]:
        """
        Cписок всех вакансий (где указан salary_from), у которых зарплата выше средней по всем вакансиям.
        Возвращает: [(vacancy_name, avg_salary), ...]
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT v.name, salary_from
                    FROM vacancies AS v
                    WHERE v.salary_from > (
                    SELECT AVG(salary_from)
                    FROM vacancies
                    )
                    ORDER BY salary_from DESC"""
                )
                rows = cast(List[Tuple[str, int]], cur.fetchall())
                return rows

    def get_vacancies_with_keyword(self, word: str) -> List[Tuple[str]]:
        """
        Вакансии, в названии которых содержится слово `word`.
        Возвращает: [(vacancy_name,), ...]
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                SELECT v.name
                FROM vacancies v
                WHERE v.name ILIKE %s
                """,
                    (f"%{word}%",),
                )
                rows = cast(List[Tuple[str]], cur.fetchall())
                return rows
