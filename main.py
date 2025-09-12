from config import config
from src.DBManager import DBManager
from src.hh_api import get_hh_data
from src.utils import create_db_and_tables, load_data_to_bd


def main():

    company_list = [
        "4649269",  # T1
        "1740",  # Яндекс
        "2748",  # Ростелеком
        "3529",  # СБЕР
        "78638",  # Т-банк
        "3776",  # MTC
        "15478",  # VK
        "80",  # Альфа банк
        "4181",  # ВТБ
        "115",  # Ай-Теко
    ]

    data = get_hh_data(company_list)
    params = config()
    create_db_and_tables("jobber", params)
    load_data_to_bd("jobber", data, params)


if __name__ == "__main__":
    # main()

    params = config()
    manager = DBManager("jobber", params)

    print(manager.get_companies_and_vacancies_count())
