import sqlite3
from enum import Enum
from typing import List, Generator, Any, Type, Dict, TypedDict

from loguru import logger
from dataclasses import dataclass
import sql_lib

# (?:(?<=-)|(?<=^))\d{2,4}(?:(?=-)|(?=\s))|(?:(?<=\s)|(?<=:))\d{2}(?:(?=:)|(?=$))


def main():
    raise NotImplemented
    # entry = Entry(a=1, b="asvqV2", c=Date(2001, 1, 1, 0, 0, 0))
    # table = Table("table1", Entry)
    # db_mgr = DBManager("db.sqlite", [table])
    # db_mgr.insert_entries([entry])


if __name__ == '__main__':
    main()
