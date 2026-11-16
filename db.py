"""Хранение книг в SQLite. База располагается рядом с модулем."""

import sqlite3
from contextlib import closing
from pathlib import Path

from logic import normalize_status, parse_book_id, validate_book

DB_PATH = Path(__file__).resolve().with_name("project.db")


def get_connection():
    """Открывает соединение с SQLite с доступом к столбцам по именам."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Создаёт таблицу books при отсутствии, не удаляя существующие записи."""
    with closing(get_connection()) as connection, connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK(length(trim(title)) > 0),
                author TEXT NOT NULL CHECK(length(trim(author)) > 0),
                genre TEXT NOT NULL CHECK(length(trim(genre)) > 0),
                status TEXT NOT NULL
                    CHECK(status IN ('в планах', 'читаю', 'прочитано'))
            )
        """)


def add_item(title: str, author: str, genre: str, status: str) -> int:
    """Добавляет проверенную книгу и возвращает ID; неверные поля — ValueError."""
    book = validate_book(title, author, genre, status)
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(
            "INSERT INTO books (title, author, genre, status) VALUES (?, ?, ?, ?)",
            (book["title"], book["author"], book["genre"], book["status"]),
        )
        return cursor.lastrowid


def get_all_items() -> list:
    """Возвращает список словарей с книгами, отсортированный по ID."""
    with closing(get_connection()) as connection:
        rows = connection.execute("SELECT * FROM books ORDER BY id").fetchall()
        return [dict(row) for row in rows]


def update_status(book_id: int, status: str) -> bool:
    """Меняет статус по ID; возвращает False, если книга не найдена.

    Некорректные ID или статус вызывают ValueError.
    """
    book_id = parse_book_id(str(book_id))
    status = normalize_status(status)
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(
            "UPDATE books SET status = ? WHERE id = ?", (status, book_id)
        )
        return cursor.rowcount > 0


def delete_item(book_id: int) -> bool:
    """Удаляет книгу по положительному ID; возвращает, найдена ли запись."""
    book_id = parse_book_id(str(book_id))
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute("DELETE FROM books WHERE id = ?", (book_id,))
        return cursor.rowcount > 0


def get_statistics() -> dict:
    """Возвращает total, read_count и genres — количества всех книг по жанрам.

    read_count учитывает только статус «прочитано»; genres учитывает все статусы.
    Для пустой базы возвращает нулевые количества и пустой словарь genres.
    """
    with closing(get_connection()) as connection:
        total = connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        read_count = connection.execute(
            "SELECT COUNT(*) FROM books WHERE status = ?", ("прочитано",)
        ).fetchone()[0]
        rows = connection.execute(
            "SELECT genre, COUNT(*) AS amount FROM books GROUP BY genre ORDER BY genre"
        ).fetchall()
        return {
            "total": total,
            "read_count": read_count,
            "genres": {row["genre"]: row["amount"] for row in rows},
        }
