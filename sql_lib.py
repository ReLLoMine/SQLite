from enum import Enum

from loguru import logger
import sqlite3
from typing import Generator, List, Any, Type, Dict


class Date:
    def __init__(self, year=1970, month=1, day=1, hour=0, minute=0, second=0):
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
        raise NotImplemented

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


class SQLParams(Enum):
    NULL = "NULL"
    NOT_NULL = "NOT NULL"
    PRIMARY_KEY = "PRIMARY KEY"
    FOREIGN_KEY = "FOREIGN KEY"
    AUTOINCREMENT = "AUTOINCREMENT"

    def __str__(self):
        return self.value


class SQLTypes(Enum):
    INT = "INT", int
    BIGINT = "BIGINT", int
    INTEGER = "INTEGER", int
    VARCHAR = "VARCHAR", str, "size"
    BOOLEAN = "BOOLEAN", bool
    FLOAT = "FLOAT", float, "p"
    DOUBLE = "DOUBLE", float, "size", "d"
    DATETIME = "DATETIME", Date

    def sql_type(self):
        return str(self)

    def py_type(self):
        return self.value[1]

    def __str__(self):
        return self.value[0]


class Field:
    def __init__(self, type: SQLTypes, *args: List[Any]):
        self.__value = type.py_type()()
        self.type = type
        self.params: List[SQLParams] = []
        self.args = list(args)

    def __add__(self, other):
        if type(other) is not SQLParams:
            raise TypeError

        self.params.append(other)
        return self

    def __str__(self):
        arguments = f"({', '.join(map(str, self.args))})" if self.args else ""
        params = " " + " ".join(map(str, self.params)) if self.params else ""
        return f"{self.type.sql_type()}{arguments}{params}"

    def __verify_type__(self, val):
        if type(val) is self.type.py_type():
            return True
        return False

    def is_primary_key(self):
        return SQLParams.PRIMARY_KEY in self.params

    def def_value(self):
        return self.__value


class INT(Field):
    def __init__(self):
        super().__init__(SQLTypes.INT)


class BIGINT(Field):
    def __init__(self):
        super().__init__(SQLTypes.BIGINT)


class INTEGER(Field):
    def __init__(self):
        super().__init__(SQLTypes.INTEGER)


class DOUBLE(Field):
    def __init__(self, size, d):
        super().__init__(SQLTypes.DOUBLE, size, d)


class FLOAT(Field):
    def __init__(self, p):
        super().__init__(SQLTypes.FLOAT, p)


class DATETIME(Field):
    def __init__(self, fsp):
        super().__init__(SQLTypes.DATETIME, fsp)


def d(v):
    print(v)
    return v


class Entry:
    def __init__(self, **kwargs):
        self.__values = {}

        fields = self.__get_fields__()

        _kwargs = dict()

        for key, val in fields.items():
            _kwargs[key] = kwargs[key] if key in kwargs else val.def_value()

        kwargs = _kwargs

        for key, value in kwargs.items():
            if key in fields:
                if type(value) is fields[key].type.py_type():
                    self.__values[key] = value

    def set_vals(self, *args, primary_key=False):
        fields = self.__get_fields__()

        for key, val in zip(filter(lambda x: not fields[x].is_primary_key() or primary_key, self.__values.keys()),
                            args):
            self.__values[key] = val

    def get_vals(self, primary_key=False):
        return [*map(lambda y: y[1], filter(lambda x: not self.__get_fields__()[x[0]].is_primary_key() or primary_key,
                                            self.__values.items()))]

    def get_fields_on_select(self):
        return self.get_fields_on_insert(primary_key=True)

    def get_fields_on_insert(self, primary_key=False):
        return ", ".join(
            f"{key}" for key, _ in filter(lambda x: not x[1].is_primary_key() or primary_key,
                                          self.__get_fields__().items()))

    def get_fields_on_create(self):
        args = lambda val: f"({', '.join(map(str, val.args))})" if val.args else ""
        return ",\n".join(f"{key} {val.type}{args(val)}" for key, val in self.__get_fields__().items())

    def __get_fields__(self) -> Dict[str, Field]:
        return {key: val for key, val in
                filter(lambda x: issubclass(type(x[1]), Field), self.__class__.__dict__.items())}

    def __iter__(self):
        return self.__values

    def __str__(self):
        return self.get_fields_on_create()

    def __setattr__(self, key, value):
        if key in self.__get_fields__():
            self.__values[key] = value
        else:
            super().__setattr__(key, value)

    def __getattribute__(self, item):
        if item in ["__dict__", "__get_fields__", "__values", "__class__"]:
            return super().__getattribute__(item)

        if item in self.__get_fields__():
            return self.__values[item]
        return super().__getattribute__(item)


class DataEntry:
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

    @classmethod
    def get_sql_fields(cls, id_field=False):
        for key, _type in cls.__get_fields(id_field=True):
            if not key == "id" or id_field:
                param = cls.__field_param(_type[0]).format(*map(str, _type[1:]))
                yield f"{key} {cls.__translate[_type[0]][0]}" + param

    @classmethod
    def __field_param(cls, _type):
        sql_type = cls.__translate[_type]
        return "({}, {})" if sql_type[2] else "({})" if sql_type[1] else ""

    @classmethod
    def get_sql_types(cls, id_field=False):
        for _type in cls.__get_types(id_field):
            yield cls.__translate[_type][0][0]

    @classmethod
    def get_names(cls, id_field=False):
        return cls.__get_py_keys(id_field)

    @classmethod
    def __get_fields(cls, id_field=False):
        for key, _type in filter(
                lambda x: not x[0].startswith("__") and not callable(x[1] and x[0] in cls.__translate),
                cls.__dict__.items()):
            if not key == "id":
                yield key, _type
            elif id_field:
                yield key, ("ID",)

    @classmethod
    def __get_py_keys(cls, id_field=False):
        for key, _ in cls.__get_fields(id_field):
            yield key

    @classmethod
    def __get_types(cls, id_field=False):
        for _, _type in cls.__get_fields(id_field):
            yield _type

    @classmethod
    def __get_py_types(cls, id_field=False):
        for _type in cls.__get_types(id_field):
            yield _type[0] if _type[0] != "ID" else int


class A(DataEntry):
    a = INT() + SQLParams.PRIMARY_KEY
    b = DOUBLE(10, 5) + SQLParams.NOT_NULL


class Table:

    def __init__(self, title, entry: Type[DataEntry]):
        raise NotImplemented

        self.title = title
        self.__entry = entry

    def entry(self, *args):
        kwargs = {key: val for key, val in zip(self.__entry.get_names(), args)}
        return self.__entry(**kwargs)

    def entry_class(self):
        return self.__entry

    def init(self):
        return f"""CREATE TABLE IF NOT EXISTS {self.title} ({", ".join(self.__entry.get_sql_fields(id_field=True))})"""

    def insert_entry_fields(self, *args):
        return f"""INSERT INTO {self.title} ({", ".join(self.__entry.get_names())}) VALUES ({", ".join(map(lambda x: f"'{x}'", args))})"""

    def get_entry_fields(self):
        return f"""SELECT * FROM {self.title}"""


class DBManager:
    def __init__(self, path: str, tables: List[Table] = None):
        raise NotImplemented

        self.db_path = path
        self.tables = {table.entry_class(): table for table in tables} or {}
        self.__open_db()
        self.__init_tables()

    def execute(self, sql, *args):
        logger.info(sql, *args)
        self.cursor.execute(sql, args)

    def get_entries(self, entry_type: Type[DataEntry]):
        _table = self.tables[entry_type]
        self.execute(_table.get_entry_fields())
        for data in self.cursor.fetchall():
            yield _table.entry(*data)

    def insert_entries(self, entries: List[DataEntry]):
        for entry in entries:
            self.execute(self.tables[entry()].insert_entry_fields(*entry))

    def __init_tables(self):
        for table in self.tables.values():
            self.execute(table.init())

    def __open_db(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def __del__(self):
        logger.info("Closing database")
        self.__save_db()
        self.__close_db()

    def __save_db(self):
        self.connection.commit()

    def __close_db(self):
        self.connection.close()
