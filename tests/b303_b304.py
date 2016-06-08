"""
Should emit:
B303 - on line 21
B304 - on line 28
"""

import sys
import something_else

def this_is_okay():
    something_else.maxint
    maxint = 3
    maxint

maxint = 3

def this_is_also_okay():
    maxint

class CustomClassWithBrokenMetaclass:
    __metaclass__ = type
    maxint = 5  # this is okay

    def this_is_also_fine(self):
        self.maxint

def this_is_wrong():
    sys.maxint
