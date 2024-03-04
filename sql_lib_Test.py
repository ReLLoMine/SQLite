import unittest
import sql_lib


class FieldTest(unittest.TestCase):
    def test_int(self):
        instance = sql_lib.INT() + sql_lib.SQLParams.PRIMARY_KEY
        self.assertEqual("INT PRIMARY KEY", str(instance))

    def test_double(self):
        instance = sql_lib.DOUBLE(10, 5) + sql_lib.SQLParams.NOT_NULL
        self.assertEqual("DOUBLE(10, 5) NOT NULL", str(instance))

    def test_date(self):
        instance = sql_lib.DATETIME(6)
        self.assertEqual("DATETIME(6)", str(instance))


class EntryTest(unittest.TestCase):
    def test(self):
        class A(sql_lib.Entry):
            a = sql_lib.INT() + sql_lib.SQLParams.PRIMARY_KEY
            b = sql_lib.DOUBLE(10, 5)
            c = sql_lib.FLOAT(5)
            d = sql_lib.DATETIME(6)

        instance = A(a=10)
        instance.b = 15.
        instance.c = 10.

        self.assertEqual(10, instance.a)
        self.assertEqual(15., instance.b)
        self.assertEqual(10., instance.c)
        self.assertEqual("1970-01-01 00:00:00", str(instance.d))
        self.assertEqual("a INT,\nb DOUBLE(10, 5),\nc FLOAT(5),\nd DATETIME(6)", instance.get_fields_on_create())
        self.assertEqual("a, b, c, d", instance.get_fields_on_select())
        self.assertEqual("b, c, d", instance.get_fields_on_insert())

    def test_set_vals(self):
        class A(sql_lib.Entry):
            id = sql_lib.INT() + sql_lib.SQLParams.PRIMARY_KEY
            a = sql_lib.INT()
            b = sql_lib.INT()

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


if __name__ == '__main__':
    unittest.main()
