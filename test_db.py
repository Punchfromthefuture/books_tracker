"""Тесты SQLite: для каждого теста используется отдельная временная база."""
import pytest
import db


@pytest.fixture
def database(tmp_path, monkeypatch):
    """Подменяет путь базы, не затрагивая пользовательский project.db."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    return db


def test_empty_database(database):
    """Новая база не содержит книг."""
    assert database.get_all_items() == []


def test_add_and_get(database):
    """Добавленная книга доступна при новом соединении."""
    book_id = database.add_item("Книга", "Автор", "Роман", "в планах")
    assert database.get_all_items() == [
        {"id": book_id, "title": "Книга", "author": "Автор", "genre": "роман", "status": "в планах"}
    ]


def test_change_status(database):
    """Статус изменяется и сохраняется в базе."""
    book_id = database.add_item("Книга", "Автор", "Роман", "читаю")
    assert database.update_status(book_id, "прочитано") is True
    assert database.get_all_items()[0]["status"] == "прочитано"


def test_missing_update(database):
    """Обновление отсутствующей книги возвращает False."""
    assert database.update_status(999, "читаю") is False


def test_delete(database):
    """Удаление существующей книги удаляет запись."""
    book_id = database.add_item("Книга", "Автор", "Роман", "читаю")
    assert database.delete_item(book_id) is True
    assert database.get_all_items() == []


def test_delete_missing(database):
    """Удаление отсутствующей книги возвращает False."""
    assert database.delete_item(999) is False


def test_statistics(database):
    """Статистика считает прочитанные книги и все книги каждого жанра."""
    database.add_item("А", "Автор", "Роман", "прочитано")
    database.add_item("Б", "Автор", "роман", "читаю")
    database.add_item("В", "Автор", "Поэзия", "прочитано")
    assert database.get_statistics() == {
        "total": 3, "read_count": 2, "genres": {"поэзия": 1, "роман": 2}
    }


def test_empty_statistics(database):
    """Пустая база возвращает нули и пустой список жанров."""
    assert database.get_statistics() == {"total": 0, "read_count": 0, "genres": {}}


def test_init_preserves_data(database):
    """Повторная инициализация не удаляет сохранённые книги."""
    database.add_item("Книга", "Автор", "Роман", "читаю")
    database.init_db()
    assert len(database.get_all_items()) == 1


def test_invalid_book_not_saved(database):
    """Некорректные данные не попадают в базу."""
    with pytest.raises(ValueError):
        database.add_item(" ", "Автор", "Роман", "читаю")
    assert database.get_all_items() == []


def test_invalid_status_preserves_record(database):
    """Некорректный статус не изменяет существующую книгу."""
    book_id = database.add_item("Книга", "Автор", "Роман", "читаю")
    with pytest.raises(ValueError):
        database.update_status(book_id, "неизвестно")
    assert database.get_all_items()[0]["status"] == "читаю"


def test_sql_text_is_data(database):
    """SQL-подобное название сохраняется как текст, а не исполняется."""
    title = "Книга'); DROP TABLE books; --"
    database.add_item(title, "Автор", "Роман", "читаю")
    assert database.get_all_items()[0]["title"] == title
