"""
Should emit:
B017 - on lines 24 and 26.
"""
import asyncio
import unittest

import pytest

CONSTANT = True


def something_else() -> None:
    for i in (1, 2, 3):
        print(i)


class Foo:
    pass


class Foobar(unittest.TestCase):
    def evil_raises(self) -> None:
        with self.assertRaises(Exception):
            raise Exception("Evil I say!")
        with pytest.raises(Exception):
            raise Exception("Evil I say!")

    def context_manager_raises(self) -> None:
        with self.assertRaises(Exception) as ex:
            raise Exception("Context manager is good")
        with pytest.raises(Exception) as pyt_ex:
            raise Exception("Context manager is good")

        self.assertEqual("Context manager is good", str(ex.exception))
        self.assertEqual("Context manager is good", str(pyt_ex.exception))

    def regex_raises(self) -> None:
        with self.assertRaisesRegex(Exception, "Regex is good"):
            raise Exception("Regex is good")
        with pytest.raises(Exception, "Regex is good"):
            raise Exception("Regex is good")

    def raises_with_absolute_reference(self):
        with self.assertRaises(asyncio.CancelledError):
            Foo()
        with pytest.raises(asyncio.CancelledError):
            Foo()
