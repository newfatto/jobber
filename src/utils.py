from typing import Any, Dict, List

import psycopg2
from psycopg2 import errors, sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_db_and_tables(database_name: str, params) -> None:
    """Функция создаёт базу данных и таблицы в PostgreSQL"""
    admin_conn = psycopg2.connect(database="postgres", **params)
    admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    try:
        with admin_conn.cursor() as cur:
            try:
                cur.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database_name)))
            except errors.InvalidCatalogName:
                print(f"База данных {database_name} не существует, пропускаем удаление.")
            cur.execute(f"CREATE DATABASE {database_name}")
            print(f'Создана база данных "{database_name}"')
    finally:
        admin_conn.close()

    with psycopg2.connect(database=database_name, **params) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            CREATE TABLE employers(
            employer_id BIGINT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            site_url TEXT,
            area VARCHAR(100),
            open_vacancies INT
            )
            """
            )

            cur.execute(
                """
            CREATE TABLE vacancies(
            vacancy_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            employer_id INT REFERENCES employers(employer_id),
            salary_from INT,
            salary_to INT,
            currency VARCHAR(10),
            area VARCHAR(100),
            url TEXT
            )
            """
            )
        conn.commit()

        print("Созданы столбцы в таблицах")


def load_data_to_bd(database_name, data, params):
    """Функция загружает полученные данные в базу данных"""
    with psycopg2.connect(database=database_name, **params) as conn:

        with conn.cursor() as cur:
            for employer in data["employers"]:
                cur.execute(
                    """
                INSERT INTO employers(employer_id, name, site_url, area, open_vacancies)
                VALUES(%s, %s, %s, %s, %s)
                """,
                    (
                        int(employer["id"]),
                        employer.get("name"),
                        employer.get("site_url"),
                        (employer.get("area") or {}).get("name"),
                        employer.get("open_vacancies"),
                    ),
                )

            for vacancy in data["vacancies"]:
                salary = vacancy.get("salary") or {}
                cur.execute(
                    """
                INSERT INTO vacancies(name, employer_id, salary_from, salary_to, currency, area, url)
                VALUES(%s, %s, %s, %s, %s, %s, %s)
                RETURNING vacancy_id
                """,
                    (
                        vacancy.get("name"),
                        int((vacancy.get("employer") or {}).get("id")),
                        salary.get("from"),
                        salary.get("to"),
                        salary.get("currency"),
                        (vacancy.get("area") or {}).get("name"),
                        vacancy.get("alternate_url"),
                    ),
                )
                conn.commit()
    print("Наполнение таблиц завершено")
