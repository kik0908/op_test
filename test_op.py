import unittest
import op


class TestOP(unittest.TestCase):
    def setUp(self):
        self.op = op.OP()

    def test_simple_inserting(self):
        self.op.insert(0, 0, 0, "abc")

        self.op.sync()
        self.assertEqual(self.op.text, ["abc"])

        self.op.insert(0, 0, 0, "def")

        self.op.sync()
        self.assertEqual(self.op.text, ["defabc"])

        self.op.insert(0, 0, 1, "klm")

        self.op.sync()
        self.assertEqual(self.op.text, ["dklmefabc"])

        self.op.insert(0, 1, 0, "123")

        self.op.sync()
        self.assertEqual(self.op.text, ["dklmefabc", "123"])

        self.op.insert(0, 1, 2, "a")

        self.op.sync()
        self.assertEqual(self.op.text, ["dklmefabc", "12a3"])

        self.op.insert(0, 0, 2, "a")

        self.op.sync()
        self.assertEqual(self.op.text, ["dkalmefabc", "12a3"])

    def test_simple_delete(self):
        self.op.insert(0, 0, 0, "abc")  # version: 1 text: abc
        self.op.sync()

        self.op.delete(1, 0, 0, 1)  # version: 2 text: bc
        self.op.sync()
        self.assertEqual(self.op.text, ["bc"])

        self.op.insert(1, 0, 0, "abc")  # version: 3 text: abcbc
        self.op.sync()

        self.op.delete(1, 0, 0, 1)  # version: 4 text: bcbc
        self.op.sync()
        self.assertEqual(self.op.text, ["bcbc"])

        self.op.delete(1, 0, 0, 1)  # version: 5 text: cbc
        self.op.sync()
        self.assertEqual(self.op.text, ["cbc"])

        self.op.delete(1, 0, 2, 1)  # version: 1 text: cb
        self.op.sync()
        self.assertEqual(self.op.text, ["cb"])

    def test_many_insert(self):
        self.op.insert(0, 0, 0, "xyz")  # version: 1 text: xyz
        self.op.insert(1, 0, 0, "def")  # version: 2 text: defxyz
        self.op.insert(2, 0, 0, "abc")  # version: 3 text: abcdefxyz
        self.assertEqual(self.op.pre(), ['abcdefxyz'])
        self.op.sync()
        self.assertEqual(self.op.text, ['abcdefxyz'])

        self.op = op.OP()

        self.op.insert(0, 0, 0, "xyz")  # version: 1 text: xyz
        self.op.insert(0, 0, 0, "def")  # version: 2 text: xyzdef
        self.op.insert(0, 0, 0, "abc")  # version: 3 text: xyzdefabc
        self.assertEqual(self.op.pre(), ['xyzdefabc'])
        self.op.sync()
        self.assertEqual(self.op.text, ['xyzdefabc'])

        self.op = op.OP()

        self.op.insert(0, 0, 0, "xyz")  # version: 1 text: xyz
        self.op.insert(1, 0, 0, "def")  # version: 2 text: defxyz
        self.op.insert(0, 0, 0, "abc")  # version: 3 text: defxyzabc
        self.assertEqual(self.op.pre(), ['defxyzabc'])
        self.op.sync()
        self.assertEqual(self.op.text, ['defxyzabc'])

        self.op = op.OP()

        self.op.insert(0, 0, 0, "xyz")  # version: 1 text: xyz
        self.op.insert(1, 0, 0, "def")  # version: 2 text: defxyz
        self.op.insert(1, 0, 0, "abc")  # version: 3 text: defabcxyz
        self.assertEqual(self.op.pre(), ['defabcxyz'])
        self.op.sync()
        self.assertEqual(self.op.text, ['defabcxyz'])

        self.op = op.OP()

        self.op.insert(0, 0, 0, "xyz")  # version: 1 text: xyz
        self.op.insert(1, 0, 0, "def")  # version: 2 text: defxyz
        self.op.insert(2, 0, 0, "abc")  # version: 3 text: abcdefxyz
        self.op.insert(0, 0, 0, "123")  # version: 4 text: abcdefxyz123
        self.op.insert(4, 0, 0, "456")  # version: 5 text: 456abcdefxyz123
        self.op.insert(2, 0, 0, "789")  # version: 6 text: 456abc789defxyz123
        self.assertEqual(self.op.pre(), ['456abc789defxyz123'])
        self.op.sync()
        self.assertEqual(self.op.text, ['456abc789defxyz123'])

    def test_many_deletes(self):
        self.op.insert(0, 0, 0, "123456789x")  # version: 1 text: 123456789x

        self.op.delete(1, 0, 0, 1)  # version: 2 text: 23456789x
        self.assertEqual(self.op.pre(), ["23456789x"])

        self.op.delete(2, 0, 3, 1)  # version: 3 text: 2346789x
        self.assertEqual(self.op.pre(), ["2346789x"])

        self.op.delete(2, 0, 4, 1)  # version: 4 text: 234789x
        self.assertEqual(self.op.pre(), ["234789x"])

        self.op.delete(4, 0, 4, 1)  # version: 5 text: 23479x
        self.assertEqual(self.op.pre(), ["23479x"])

        self.op.delete(4, 0, 5, 1)  # version: 6 text: 2347x
        self.assertEqual(self.op.pre(), ["2347x"])

        self.op.delete(3, 0, 7, 1)  # version: 7 text:  2347
        self.assertEqual(self.op.pre(), ["2347"])

        self.op.delete(6, 0, 0, 1)  # version: 7 text:  347
        self.assertEqual(self.op.pre(), ["347"])

        self.op.delete(6, 0, 1, 1)  # version: 7 text: 47
        self.assertEqual(self.op.pre(), ["47"])

        self.op.sync()
        self.assertEqual(self.op.text, ['47'])

    def test_many_operations_1(self):
        self.op.insert(0, 0, 0, "xyz")  # version: 1 text: xyz
        self.op.insert(0, 0, 0, "def")  # version: 2 text: xyzdef
        self.op.insert(0, 0, 0, "abc")  # version: 3 text: xyzdefabc
        self.op.delete(3, 0, 8, 1)  # version: 4 text: xyzdefab
        self.assertEqual(self.op.pre(), ['xyzdefab'])
        self.op.delete(3, 0, 1, 1)  # version: 5 text: xzdefab
        self.op.delete(5, 0, 0, 1)  # version: 6 text: zdefab
        self.op.delete(5, 0, 1, 1)  # version: 7 text: defab
        self.op.insert(6, 0, 5, "1234")  # version: 8 text: defa1234b
        self.op.insert(7, 0, 5, "qwrt")  # version: 9 text: defa1234bqwrt

        self.op.sync()
        self.assertEqual(self.op.text, ['defa1234bqwrt'])

        self.op = op.OP()
        self.op.insert(0, 0, 0, "123!qwerty")  # version: 1 text: 123!qwerty
        self.op.insert(1, 0, 3, "?")  # version: 2 text: 123?!qwerty
        self.op.delete(1, 0, 3, 1)  # version: 3 text: 123?qwerty
        self.assertEqual(self.op.pre(), ['123?qwerty'])
        self.op.insert(1, 0, 3, "@")  # version: 4 text: 123?@qwerty
        self.op.delete(3, 0, 3, 1)  # version: 5 text: 123@qwerty
        self.op.sync()
        self.assertEqual(self.op.text, ['123@qwerty'])

    def test_many_operations_2(self):
        self.op.insert(0, 0, 0, "Lorem ipsum")  # version: 1 text: Lorem ipsum
        self.op.insert(1, 0, 11, "123")  # version: 2 text: Lorem ipsum123
        self.op.delete(1, 0, 2, 3)  # version: 3 text: Lo ipsum123
        self.op.sync()
        self.assertEqual(self.op.text, ["Lo ipsum123"])
        self.op.delete(0, 0, 4, 4)  # version: 1 text: Lo i123
        self.op.insert(1, 0, 0, "qwe")  # version: 2 text: qweLo i123
        self.op.insert(0, 0, 0, "123")  # version: 3 text: qwe123Lo i123
        self.assertEqual(self.op.pre(), ["qwe123Lo i123"])

    def test_intersections_delete_1(self):
        # When
        # ..----.........
        # .......~~~~~~..
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 0, 3)  # version: 2 text: 456789
        self.op.delete(1, 0, 3, 3)  # version: 3 text: 789
        self.assertEqual(self.op.pre(), ["789"])

        # When
        # .........-----..
        # ..~~~~~~........
        self.op.insert(3, 0, 0, "123456")  # version: 4 text: 123456789
        self.op.delete(4, 0, 3, 3)  # version: 5 text: 123789
        self.op.delete(4, 0, 0, 3)  # version: 6 text: 789
        self.assertEqual(self.op.pre(), ["789"])

        self.op.sync()
        self.assertEqual(self.op.text, ["789"])

    def test_intersections_delete_2(self):
        # when
        # ...~~~~~....
        # .---------..
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 0, 6)  # version: 2 text: 789
        self.op.delete(1, 0, 1, 4)  # version: 3 text: 789
        self.assertEqual(self.op.pre(), ["789"])
        # when
        # ..~~~~~..
        # ..-----..
        self.op.insert(3, 0, 0, "123456")  # version: 4 text: 123456789
        self.op.delete(4, 0, 0, 5)  # version: 5 text: 6789
        self.op.delete(4, 0, 0, 5)  # version: 6 text: 6789
        self.assertEqual(self.op.pre(), ["6789"])

        # when
        # ..~~~~~...
        # ..-------.
        self.op.insert(6, 0, 0, "12345")  # version: 7 text: 123456789
        self.op.delete(7, 0, 0, 5)  # version: 8 text: 6789
        self.op.delete(7, 0, 0, 3)  # version: 9 text: 6789
        self.assertEqual(self.op.pre(), ["6789"])

        # when
        # ...~~~~~~..
        # .--------..
        self.op.insert(9, 0, 0, "12345")  # version: 10 text: 123456789
        self.op.delete(10, 0, 0, 5)  # version: 11 text: 6789
        self.op.delete(10, 0, 2, 3)  # version: 12 text: 6789
        self.assertEqual(self.op.pre(), ["6789"])
        self.op.sync()
        self.assertEqual(self.op.text, ["6789"])

    def test_intersections_delete_3(self):
        # When
        # .------.....
        # ...~~~~~~~..
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 0, 4)  # version: 2 text: 56789
        self.op.delete(1, 0, 1, 4)  # version: 3 text: 6789
        self.assertEqual(self.op.pre(), ["6789"], msg="case 1")

        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 0, 4)  # version: 2 text: 56789
        self.op.delete(1, 0, 2, 5)  # version: 3 text: 89
        self.assertEqual(self.op.pre(), ["89"])

        # When
        # .-----.....
        # .~~~~~~~~..
        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 0, 4)  # version: 2 text: 56789
        self.op.delete(1, 0, 0, 5)  # version: 3 text: 6789
        self.assertEqual(self.op.pre(), ["6789"], msg="case 2")

        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 0, 4)  # version: 2 text: 56789
        self.op.delete(1, 0, 0, 9)  # version: 3 text:
        self.assertEqual(self.op.pre(), [""])

        # When
        # ..----........
        # .....~~~~~~...
        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 0, 4)  # version: 2 text: 56789
        self.op.delete(1, 0, 3, 3)  # version: 3 text: 789
        self.assertEqual(self.op.pre(), ["789"])

        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 0, 4)  # version: 2 text: 56789
        self.op.delete(1, 0, 3, 1)  # version: 3 text: 56789
        self.assertEqual(self.op.pre(), ["56789"])

        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 0, 4)  # version: 2 text: 56789
        self.op.delete(1, 0, 3, 2)  # version: 3 text: 6789
        self.assertEqual(self.op.pre(), ["6789"], msg="case 3")

    def test_intersections_delete_4(self):
        # When
        # ...------...
        # .~~~~~~~~~~.
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 3, 4)  # version: 2 text: 12389
        self.op.delete(1, 0, 1, 8)  # version: 3 text: 1
        self.assertEqual(self.op.pre(), ["1"])

        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 3, 1)  # version: 2 text: 12356789
        self.op.delete(1, 0, 0, 9)  # version: 3 text:
        self.assertEqual(self.op.pre(), [""])

        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 3, 1)  # version: 2 text: 12356789
        self.op.delete(1, 0, 3, 1)  # version: 3 text: 12356789
        self.assertEqual(self.op.pre(), ["12356789"])

        # When
        # ...--------..
        # .~~~~~~~~~~..
        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 3, 3)  # version: 2 text: 123789
        self.op.delete(1, 0, 0, 6)  # version: 3 text: 789
        self.assertEqual(self.op.pre(), ["789"])

        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 3, 6)  # version: 2 text: 123
        self.op.delete(1, 0, 0, 9)  # version: 3 text:
        self.assertEqual(self.op.pre(), [""])

        # When
        # ...------..
        # .~~~~~~....
        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 3, 6)  # version: 2 text: 123
        self.op.delete(1, 0, 0, 5)  # version: 3 text:
        self.assertEqual(self.op.pre(), [""])

        self.op = op.OP()
        self.op.insert(0, 0, 0, "123456789")  # version: 1 text: 123456789
        self.op.delete(1, 0, 3, 3)  # version: 2 text: 123789
        self.op.delete(1, 0, 1, 4)  # version: 3 text: 1789
        self.assertEqual(self.op.pre(), ["1789"])


if __name__ == '__main__':
    unittest.main()
