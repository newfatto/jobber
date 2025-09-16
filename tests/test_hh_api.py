from unittest.mock import Mock, patch
from src.hh_api import get_hh_data

@patch("src.hh_api.requests.get")
def test_get_hh_data_success(mock_get) -> None:
    """Возвращается dict с ключами employers и vacancies при успехе запросов."""
    # Первый вызов — /employers/{id}
    employer_resp = Mock()
    employer_resp.ok = True
    employer_resp.json.return_value = {"id": "123", "name": "Test Company"}

    # Второй вызов — /vacancies
    vacancies_resp = Mock()
    vacancies_resp.ok = True
    vacancies_resp.json.return_value = {"items": [], "pages": 0}

    def side_effect(url, *args, **kwargs):
        return employer_resp if "employers" in url else vacancies_resp

    mock_get.side_effect = side_effect

    result = get_hh_data(["123"], max_pages=1)
    assert isinstance(result, dict)
    assert "employers" in result and "vacancies" in result
