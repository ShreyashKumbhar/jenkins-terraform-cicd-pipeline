import unittest
from app.calculator import add, multiply, is_even


class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_multiply(self):
        self.assertEqual(multiply(4, 5), 20)

    def test_is_even(self):
        self.assertTrue(is_even(10))
        self.assertFalse(is_even(7))


if __name__ == "__main__":
    unittest.main()
