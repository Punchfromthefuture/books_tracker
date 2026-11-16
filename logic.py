"""Проверка данных, фильтрация и форматирование списка книг."""

STATUSES = ("в планах", "читаю", "прочитано")


def clean_text(value: str, field: str) -> str:
    """Удаляет лишние пробелы; вызывает ValueError для пустого текста."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Поле «{field}» не должно быть пустым.")
    return " ".join(value.split())


def normalize_status(status: str) -> str:
    """Нормализует статус; неизвестный статус вызывает ValueError."""
    result = clean_text(status, "Статус").lower()
    if result not in STATUSES:
        raise ValueError("Допустимые статусы: в планах, читаю, прочитано.")
    return result


def validate_book(title: str, author: str, genre: str, status: str) -> dict:
    """Возвращает проверенные поля книги; ошибки вызывают ValueError."""
    return {
        "title": clean_text(title, "Название"),
        "author": clean_text(author, "Автор"),
        "genre": clean_text(genre, "Жанр").casefold(),
        "status": normalize_status(status),
    }


def parse_book_id(value: str) -> int:
    """Преобразует строку в положительный ID; иначе вызывает ValueError."""
    try:
        book_id = int(value)
    except (TypeError, ValueError):
        raise ValueError("ID должен быть положительным целым числом.") from None
    if book_id <= 0:
        raise ValueError("ID должен быть положительным целым числом.")
    return book_id


def filter_books(books: list, status: str = None, genre: str = None) -> list:
    """Возвращает новый список с фильтрами по статусу и точному названию жанра.

    Если заданы оба фильтра, применяются оба. Исходный список не изменяется.
    Жанр сравнивается без учёта регистра; неверный статус вызывает ValueError.
    """
    target_status = normalize_status(status) if status is not None else None
    target_genre = clean_text(genre, "Жанр").casefold() if genre is not None else None
    return [
        book for book in books
        if (target_status is None or book["status"] == target_status)
        and (target_genre is None or book["genre"].casefold() == target_genre)
    ]


def format_book(book: dict) -> str:
    """Возвращает строку с ID, названием, автором, жанром и статусом книги."""
    return (
        f"ID {book['id']} | {book['title']} | {book['author']} | "
        f"{book['genre']} | {book['status']}"
    )
