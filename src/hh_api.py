from typing import Any, Dict, List

import requests


def get_hh_data(company_list: List[str]) -> List[Dict[str, Any]] or None:
    """Получает данные о компаниях и их вакансиях с hh.ru."""
    employers = []
    vacancies = []
    data = []
    headers = {
        "HH-User-Agent": "jobber/1.0 (newfatto@gmail.com)",
        "Accept": "application/json",
    }

    try:
        for company in company_list:
            url = f"https://api.hh.ru/employers/{company}"
            resp = requests.get(url, headers=headers, allow_redirects=False, timeout=15)
            if resp.ok:
                employer = resp.json()
                employer.pop("branded_description", None)  # убираем содержимое поля "branded_description"
                employers.append(employer)

                page = 0
                while page < 2:
                    params = {"employer_id": company, "per_page": 20, "page": page}
                    resp = requests.get("https://api.hh.ru/vacancies", params=params, headers=headers, timeout=15)

                    if not resp.ok:
                        print(f"Неожиданный ответ: {resp.text[:200]}...")
                        break

                    payload = resp.json()
                    items = payload.get("items", [])
                    vacancies.extend(items)

                    if page >= payload.get("pages", 0) - 1:
                        break
                    page += 1

                data = {"employers": employers, "vacancies": vacancies}

        print("Данные от hh получены")
        return data

    except Exception as e:
        print(f"Не удалось выполнить запрос. Ошибка: {e}")
        return None
