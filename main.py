"""Консольный интерфейс приложения «Учёт прочитанных книг»."""

import sqlite3

import db
import logic


def choose_status() -> str:
    """Запрашивает один из трёх статусов; неверный выбор вызывает ValueError."""
    print("1. В планах\n2. Читаю\n3. Прочитано")
    choice = input("Выберите статус: ").strip()
    statuses = {"1": "в планах", "2": "читаю", "3": "прочитано"}
    if choice not in statuses:
        raise ValueError("Нужно выбрать статус от 1 до 3.")
    return statuses[choice]


def show_books(books: list):
    """Печатает список книг или сообщение об отсутствии записей."""
    if not books:
        print("Книги не найдены.")
        return
    for book in books:
        print(logic.format_book(book))


def add_book():
    """Запрашивает поля книги, сохраняет запись и показывает её ID."""
    title = input("Название: ")
    author = input("Автор: ")
    genre = input("Жанр: ")
    status = choose_status()
    book_id = db.add_item(title, author, genre, status)
    print(f"Книга добавлена. ID: {book_id}")


def change_status():
    """Изменяет статус существующей книги по введённому ID."""
    book_id = logic.parse_book_id(input("ID книги: "))
    status = choose_status()
    if db.update_status(book_id, status):
        print("Статус изменён.")
    else:
        print("Книга с таким ID не найдена.")


def delete_book():
    """Удаляет книгу по ID после явного подтверждения пользователя."""
    book_id = logic.parse_book_id(input("ID книги для удаления: "))
    if input("Подтвердите удаление (да): ").strip().casefold() != "да":
        print("Удаление отменено.")
        return
    print("Книга удалена." if db.delete_item(book_id) else "Книга с таким ID не найдена.")


def show_statistics():
    """Выводит число всех и прочитанных книг, а также распределение по жанрам."""
    statistics = db.get_statistics()
    print(f"Всего книг: {statistics['total']}")
    print(f"Прочитано книг: {statistics['read_count']}")
    print("Жанры (все статусы):")
    if not statistics["genres"]:
        print("Нет данных.")
    for genre, count in statistics["genres"].items():
        print(f"  {genre}: {count}")


def main():
    """Инициализирует БД и выполняет команды меню с обработкой ошибок."""
    try:
        db.init_db()
    except sqlite3.Error as error:
        print(f"Не удалось открыть базу данных: {error}")
        return

    while True:
        print("\n=== Учёт прочитанных книг ===")
        print("1. Добавить книгу")
        print("2. Показать все книги")
        print("3. Фильтр по статусу")
        print("4. Фильтр по жанру")
        print("5. Изменить статус книги")
        print("6. Удалить книгу по ID")
        print("7. Статистика")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "0":
                print("До свидания!")
                return
            elif choice == "1":
                add_book()
            elif choice == "2":
                show_books(db.get_all_items())
            elif choice == "3":
                status = choose_status()
                show_books(logic.filter_books(db.get_all_items(), status=status))
            elif choice == "4":
                genre = input("Введите жанр целиком: ")
                show_books(logic.filter_books(db.get_all_items(), genre=genre))
            elif choice == "5":
                change_status()
            elif choice == "6":
                delete_book()
            elif choice == "7":
                show_statistics()
            else:
                print("Неизвестный пункт меню.")
        except ValueError as error:
            print(f"Ошибка ввода: {error}")
        except sqlite3.Error as error:
            print(f"Ошибка базы данных: {error}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nРабота завершена.")
