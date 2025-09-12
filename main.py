from typing import Optional

from config import config
from src.DBManager import DBManager
from src.hh_api import get_hh_data
from src.settings import company_list, database_name
from src.utils import create_db_and_tables, load_data_to_bd


def format_salary(
    s_from: Optional[int],
    s_to: Optional[int] = None,
    currency: Optional[str] = None,
) -> str:
    """Форматирует зарплату для человекочитаемого вывода."""
    if s_from is None and s_to is None:
        return "не указана"
    if s_from is not None and s_to is not None and s_from != s_to:
        cur = f" {currency}" if currency else ""
        return f"{s_from:,}–{s_to:,}{cur}".replace(",", " ")
    cur = f" {currency}" if currency else ""
    return f"{s_from or s_to:,}{cur}".replace(",", " ")


def print_title(text: str) -> None:
    """Печатает заголовок блока в консоли."""
    print("\n" + "—" * len(text))
    print(text)
    print("—" * len(text))


def main() -> None:
    """Главная функция, запускающая пользовательский интерфейс"""

    print("Приветствую Вас в программе JOBBER!\n" "Происходит обновление данных о вакансиях...")

    params = config()

    # Получаем данные из HH (словарь с ключами 'employers' и 'vacancies')
    data = get_hh_data(company_list)

    # Создаём БД и таблицы
    create_db_and_tables(database_name, params)

    # Загружаем данные, полученные от hh, в созданные таблицы базы данных
    load_data_to_bd(database_name, data, params)

    # Создаём менеджер для работы с вакансиями (экземпляр класса DBManager)
    db = DBManager(database_name, params)

    print("Всё готово.")

    MENU = """
    Выберите действие:
      1 — Список компаний и число вакансий каждой компании
      2 — Все вакансии: компания • вакансия • зарплата • ссылка
      3 — Средняя зарплата по вакансиям (только вакансии с указанной зарплатой)
      4 — Вакансии с зарплатой выше средней (только вакансии с указанной зарплатой)
      5 — Поиск вакансий по ключевому слову
      0 — Выход
    > """
    while True:
        choice = input(MENU).strip()
        if choice == "0":
            print("Всего доброго!")
            return

        try:
            if choice == "1":
                rows_companies = db.get_companies_and_vacancies_count()
                print_title("Компании и количество их вакансий")
                if not rows_companies:
                    print("Ничего не найдено.")
                for name, cnt in rows_companies:
                    print(f"• {name}: {cnt}")

            elif choice == "2":
                rows_all = db.get_all_vacancies()
                print_title("Все вакансии")
                if not rows_all:
                    print("Ничего не найдено.")
                for vac_name, company, salary_from, url in rows_all:
                    salary_txt = format_salary(salary_from)
                    print(f"• {company} — {vac_name} — {salary_txt}\n  {url}")

            elif choice == "3":
                rows_avg = db.get_avg_salary()
                print_title("Средняя зарплата по вакансиям (где указана)")
                if not rows_avg:
                    print("Ничего не найдено.")
                for vac_name, avg in rows_avg:
                    print(f"• {vac_name}: {round(avg)}")

            elif choice == "4":
                rows_hi = db.get_vacancies_with_higher_salary()
                print_title("Вакансии с зарплатой выше средней")
                if not rows_hi:
                    print("Ничего не найдено.")
                for vac_name, s in rows_hi:
                    print(f"• {vac_name}: {s}")

            elif choice == "5":
                word = input("Ключевое слово (например, аналитик): ").strip()
                rows_kw = db.get_vacancies_with_keyword(word)
                print_title(f'Вакансии, содержащие "{word}"')
                if not rows_kw:
                    print("Ничего не найдено.")
                for (vac_name,) in rows_kw:
                    print(f"• {vac_name}")

            else:
                print("Не знаю такой команды. Попробуйте ещё раз.")

        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")


if __name__ == "__main__":
    main()
