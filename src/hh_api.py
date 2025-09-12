import time
from typing import Any, Dict, List, Optional

import requests


def get_hh_data(
    company_list: List[str],
    *,
    per_page: int = 100,
    max_pages: int = 10,
    max_vacancies_per_employer: int = 1000,
    pause_sec: float = 0.3,
) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """Получает данные о компаниях и их вакансиях с hh.ru.

    Возвращает dict: {"employers": [...], "vacancies": [...]}
    Или None при фатальной ошибке.
    """
    employers = []
    vacancies = []
    headers = {
        "HH-User-Agent": "jobber/1.0 (newfatto@gmail.com)",
        "Accept": "application/json",
    }

    try:
        for company in company_list:
            url = f"https://api.hh.ru/employers/{company}"
            resp = requests.get(url, headers=headers, allow_redirects=False, timeout=15)

            if not resp.ok:
                print(f"[employer] {company}: {resp.status_code} {resp.reason}")
                continue

            employer = resp.json()
            employer.pop("branded_description", None)  # убираем содержимое поля "branded_description"
            employers.append(employer)

            page = 0
            got_for_employer = 0
            backoff = 0.5
            while page < max_pages and got_for_employer < max_vacancies_per_employer:
                params = {"employer_id": company, "per_page": per_page, "page": page}
                resp = requests.get("https://api.hh.ru/vacancies", params=params, headers=headers, timeout=15)

                if resp.status_code == 429:
                    # лимит — подождём и повторим текущую страницу
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 8.0)
                    continue

                if not resp.ok:
                    print(f"[vacancies] {company} p{page}: {resp.status_code} {resp.reason}")
                    break

                payload = resp.json()
                items = payload.get("items", [])
                vacancies.extend(items)
                got_for_employer += len(items)

                pages_total = payload.get("pages", 0)
                page += 1
                if page >= pages_total:
                    break

                time.sleep(pause_sec)

        print("Данные о компаниях и вакансиях получены...")
        return {"employers": employers, "vacancies": vacancies}

    except Exception as e:
        print(f"Не удалось выполнить запрос. Ошибка: {e}")
        return None
