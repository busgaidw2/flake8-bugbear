from pathlib import Path
import unittest

from bugbear import BugBearChecker, B001


class BugbearTestCase(unittest.TestCase):
    maxDiff = None

    def test_b001(self):
        filename = Path(__file__).absolute().parent / 'b001.py'
        bbc = BugBearChecker(filename=str(filename))
        errors = list(bbc.run())
        self.assertEqual(
            errors,
            [B001(8, 0), B001(40, 4)],
        )


if __name__ == '__main__':
    unittest.main()
