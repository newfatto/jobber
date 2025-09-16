from main import format_salary

def test_format_salary_none() -> None:
    """Если зарплата не указана — возвращается 'не указана'."""
    assert format_salary(None, None) == "не указана"

def test_format_salary_from_only() -> None:
    """Форматирование только нижней границы зарплаты."""
    assert format_salary(100000) == "100 000"

def test_format_salary_range_with_currency() -> None:
    """Форматирование диапазона с валютой и разделителями тысяч."""
    assert format_salary(100000, 150000, "RUR") == "100 000–150 000 RUR"

def test_format_salary_single_value_when_equal() -> None:
    """Если from == to, функция печатает одно число."""
    assert format_salary(120000, 120000, "RUR") == "120 000 RUR"

def test_format_salary_to_only() -> None:
    """Если указана только верхняя граница — печатается она."""
    assert format_salary(None, 90000, "RUR") == "90 000 RUR"
