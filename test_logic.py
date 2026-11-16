"""Модульные тесты проверки данных и фильтрации."""
import pytest
import logic


@pytest.fixture
def books():
    """Возвращает независимый набор книг для фильтрации."""
    return [
        {"id": 1, "title": "Книга А", "author": "Автор А", "genre": "роман", "status": "прочитано"},
        {"id": 2, "title": "Книга Б", "author": "Автор Б", "genre": "фантастика", "status": "читаю"},
        {"id": 3, "title": "Книга В", "author": "Автор В", "genre": "роман", "status": "в планах"},
    ]


def test_validate_book():
    """Проверяет нормализацию всех полей книги."""
    assert logic.validate_book("  Моя   книга ", " Автор ", " РОМАН ", " ЧИТАЮ ") == {
        "title": "Моя книга", "author": "Автор", "genre": "роман", "status": "читаю"
    }


@pytest.mark.parametrize("field", ["title", "author", "genre"])
def test_empty_fields(field):
    """Проверяет запрет пустого названия, автора и жанра."""
    fields = dict(title="Название", author="Автор", genre="Жанр", status="читаю")
    fields[field] = "   "
    with pytest.raises(ValueError):
        logic.validate_book(**fields)


def test_invalid_status():
    """Проверяет запрет неизвестного статуса."""
    with pytest.raises(ValueError):
        logic.normalize_status("брошено")


def test_parse_id():
    """Проверяет преобразование корректного ID."""
    assert logic.parse_book_id(" 12 ") == 12


@pytest.mark.parametrize("value", ["0", "-1", "abc", "1.5", ""])
def test_invalid_id(value):
    """Проверяет отклонение некорректного ID."""
    with pytest.raises(ValueError):
        logic.parse_book_id(value)


def test_status_filter(books):
    """Проверяет фильтр статуса без изменения исходного списка."""
    assert [b["id"] for b in logic.filter_books(books, status="прочитано")] == [1]
    assert len(books) == 3


def test_genre_filter(books):
    """Проверяет сравнение жанра без учёта регистра."""
    assert [b["id"] for b in logic.filter_books(books, genre=" РОМАН ")] == [1, 3]


def test_combined_filter(books):
    """Проверяет одновременное применение двух фильтров."""
    assert [b["id"] for b in logic.filter_books(books, genre="роман", status="в планах")] == [3]


def test_no_matches(books):
    """Проверяет отсутствие совпадений."""
    assert logic.filter_books(books, genre="поэзия") == []


def test_format_book(books):
    """Проверяет состав строки отображения книги."""
    assert logic.format_book(books[0]) == "ID 1 | Книга А | Автор А | роман | прочитано"
