import psycopg2


class DBManager:

    def __init__(self, database_name, params):
        self.db = database_name
        self.params = params

    def connect(self):
        return psycopg2.connect(database=self.db, **self.params)

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании."""
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
                return cur.fetchall()

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию."""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT v.name, e.name, v.salary_from, v.url
                FROM vacancies AS v
                JOIN employers AS e
                USING(employer_id)"""
                )
                return cur.fetchall()

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям, для которых указана зарплата."""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT v.name, AVG(salary_from) AS avg_salary
                FROM vacancies AS v
                WHERE salary_from IS NOT NULL
                GROUP BY v.name
                ORDER BY avg_salary DESC"""
                )
                return cur.fetchall()

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        Для вакансий, у которых указана зарплата"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT v.name, salary_from
                FROM vacancies AS v
                WHERE v.salary_from > (
                    SELECT AVG(salary_from)
                    FROM vacancies
                )"""
                )
                return cur.fetchall()

    def get_vacancies_with_keyword(self, word: str):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python."""
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
                return cur.fetchall()


if __name__ == "__main__":
    from config import config
