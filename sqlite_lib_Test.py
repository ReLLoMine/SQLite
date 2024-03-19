import unittest
import sqlite_lib as sql_lib


class FieldTest(unittest.TestCase):
    def test_int(self):
        instance = sql_lib.INTEGER() + sql_lib.SQLParams.PRIMARY_KEY
        self.assertEqual("INTEGER PRIMARY KEY", str(instance))

    def test_double(self):
        instance = sql_lib.REAL() + sql_lib.SQLParams.NOT_NULL
        self.assertEqual("REAL NOT NULL", str(instance))

    def test_date(self):
        instance = sql_lib.DATE()
        self.assertEqual("DATE", str(instance))


class EntryTest(unittest.TestCase):
    def test_set_get_attr(self):
        class A(sql_lib.Entry):
            a = sql_lib.INTEGER() + sql_lib.SQLParams.PRIMARY_KEY
            b = sql_lib.REAL()
            c = sql_lib.REAL()
            d = sql_lib.DATE()

        instance = A(a=10)
        instance.b = 15.
        instance.c = 10.

        self.assertEqual(10, instance.a)
        self.assertEqual(15., instance.b)
        self.assertEqual(10., instance.c)
        self.assertEqual("1970-01-01 00:00:00", str(instance.d))
        self.assertEqual("a INTEGER PRIMARY KEY,\nb REAL,\nc REAL,\nd DATE",
                         instance.get_fields_on_create())
        self.assertEqual("a, b, c, d", instance.get_fields_on_select())
        self.assertEqual("b, c, d", instance.get_fields_on_insert())

    def test_set_vals(self):
        class A(sql_lib.Entry):
            id = sql_lib.INTEGER() + sql_lib.SQLParams.PRIMARY_KEY
            a = sql_lib.INTEGER()
            b = sql_lib.INTEGER()

        instance = A(a=1)
        self.assertEqual(0, instance.id)
        self.assertEqual(1, instance.a)
        self.assertEqual(0, instance.b)

        instance.set_vals(2, 1)
        self.assertEqual(0, instance.id)
        self.assertEqual(2, instance.a)
        self.assertEqual(1, instance.b)

        instance.set_vals(1, 3, primary_key=True)
        self.assertEqual(1, instance.id)
        self.assertEqual(3, instance.a)
        self.assertEqual(1, instance.b)

        self.assertEqual([1, 3, 1], instance.get_vals(primary_key=True))
        self.assertEqual([3, 1], instance.get_vals(primary_key=False))


class TableTest(unittest.TestCase):
    def test_init(self):
        class A(sql_lib.Entry):
            id = sql_lib.INTEGER() + sql_lib.SQLParams.PRIMARY_KEY
            a = sql_lib.INTEGER()
            b = sql_lib.INTEGER()

        table = sql_lib.Table("test", A)

        self.assertEqual(
            "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY,\na INTEGER,\nb INTEGER)",
            table.init())

    def test_insert(self):
        class A(sql_lib.Entry):
            id = sql_lib.INTEGER() + sql_lib.SQLParams.PRIMARY_KEY
            a = sql_lib.INTEGER()
            b = sql_lib.INTEGER()

        table = sql_lib.Table("test", A)
        entry = A().set_vals(1, 2, 3, primary_key=True)

        self.assertEqual(
            "INSERT INTO test (id, a, b) VALUES (1, 2, 3)",
            table.insert_entry(entry, pk=True))


if __name__ == '__main__':
    unittest.main()
