import sqlite3
from enum import Enum
from typing import List, Generator, Any, Type, Dict, TypedDict

from loguru import logger
from dataclasses import dataclass
from sqlite_lib import TEXT, DATE, DBManager, SQLParams, Table, Date, INTEGER, Entry


# (?:(?<=-)|(?<=^))\d{2,4}(?:(?=-)|(?=\s))|(?:(?<=\s)|(?<=:))\d{2}(?:(?=:)|(?=$))


def main():
    # Создание таблицы и записи
    class User(Entry):
        id = INTEGER() + SQLParams.PRIMARY_KEY + SQLParams.AUTOINCREMENT
        username = TEXT()
        created_at = DATE()

    # Инициализация базы данных
    db = DBManager('database.db', tables=[Table('users', User)])

    # Добавление записи
    user = User(username="john_doe", created_at=Date())
    db.insert_entries([user])

    # Получение всех пользователей
    for user in db.get_entries(User):
        print(user.get_vals())


if __name__ == '__main__':
    main()
