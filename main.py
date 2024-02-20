import sqlite3
from typing import List, Generator, Any

from loguru import logger
from dataclasses import dataclass


# (?:(?<=-)|(?<=^))\d{2,4}(?:(?=-)|(?=\s))|(?:(?<=\s)|(?<=:))\d{2}(?:(?=:)|(?=$))

def entrywrapper(cls=None):
    def wrap(cls):
        pass

    return wrap(cls)


class Date:
    def __init__(self, year, month, day, hour, minute, second):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

        if [*self.__check_vals__()]:
            raise ValueError

    @staticmethod
    def fromstr(string, format):
        pass

    def __str__(self):
        return f"{self.year}-{self.month:0>2}-{self.day:0>2} {self.hour:0>2}:{self.minute:0>2}:{self.second:0>2}"

    def __check_day__(self) -> bool:
        if self.month == 2:
            return 1 <= self.day <= (28 if self.year % 4 else 29)
        elif self.month in (1, 3, 5, 7, 8, 10, 12):
            return 1 <= self.day <= 31
        else:
            return 1 <= self.day <= 30

    def __check_vals__(self) -> Generator[str, None, None]:
        vals = {
            not 1000 <= self.year <= 9999: "year",
            not 1 <= self.month <= 12: "month",
            not self.__check_day__(): "day",
            not 0 <= self.hour <= 23: "hour",
            not 0 <= self.minute <= 59: "minute",
            not 0 <= self.second <= 59: "second"
        }

        for _, val in filter(lambda x: x[0], vals.items()):
            yield val


class DataEntry:
    __translate = {
        str: "VARCHAR",
        bool: "BOOL",
        int: "INT",

    }

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__get_py_keys() and type(value) in self.__get_py_types():
                self.__dict__[key] = value
            else:
                raise TypeError(str([*self.__get_py_keys(), *self.__get_py_types()]))

    def __str__(self):
        return ", ".join(map(str, self))

    def __iter__(self):
        for key in self.__get_py_keys():
            yield self.__dict__[key]

    def get_sql_types(self):
        pass

    def get_names(self):
        return [*self.__get_py_keys()]

    def __get_py_keys(self):
        for key, _ in filter(lambda x: not x[0].startswith("__") and not callable(x[1]),
                             self.__class__.__dict__.items()):
            yield key

    def __get_py_types(self):
        for key in self.__get_py_keys():
            yield self.__class__.__dict__[key][0]


class Entry(DataEntry):
    a = int,
    b = str, 256
    c = Date,


class Table:
    def __init__(self, title, entry: Entry):
        self.title = title
        self.entry = entry

    def init_table(self):
        return f"""CREATE TABLE IF NOT EXISTS {self.title} ({1})"""

    def get_entry_fields(self):
        pass


class DBManager:
    def __init__(self, path):
        self.db_path = path
        self.connection: sqlite3.Connection = None
        self.cursor: sqlite3.Cursor = None

    def __open_db__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def __save_db__(self):
        self.connection.commit()

    def __close_db__(self):
        self.connection.close()


def main():
    a = Entry(a=1, b="asd", c=Date(2001, 1, 1, 0, 0, 0))
    print(a.get_names())


if __name__ == '__main__':
    main()
