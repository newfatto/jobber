from src.hh_api import get_hh_data


def main():

    company_list = [
        "4649269",  # T1
        "1740",  # Яндекс
        # '2748', #Ростелеком
        # '3529', #СБЕР
        # '78638', #Т-банк
        # '3776', #MTC
        # '15478', #VK
        # '80', #Альфа банк
        # '4181', #ВТБ
        # '115' #Ай-Теко
    ]

    data = get_hh_data(company_list)

    pass


if __name__ == "__main__":
    main()
