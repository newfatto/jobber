from typing import Any, Dict, List

import psycopg2
from psycopg2 import errors, sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from config import config
from src.hh_api import get_hh_data


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
            employer_id SERIAL PRIMARY KEY,
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
            salary INT,
            currency VARCHAR(10),
            area VARCHAR(100),
            url TEXT
            )
            """
            )
        conn.commit()

        print("Созданы столбцы в таблицах")


def load_data_to_bd():
    """Функция загружает полученные данные в базу данных"""
    pass
