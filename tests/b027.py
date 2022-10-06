import abc
from abc import ABC
from abc import abstractmethod
from abc import abstractmethod as notabstract

"""
Should emit:
B025 - on lines 13, 16, 19, 23, 31
"""


class AbstractClass(ABC):
    def empty_1(self):  # error
        ...

    def empty_2(self):  # error
        pass

    def empty_3(self):  # error
        """docstring"""
        ...

    def empty_4(self):  # error
        """multiple ellipsis/pass"""
        ...
        pass
        ...
        pass

    @notabstract
    def empty_5(self):  # error
        ...

    @abstractmethod
    def abstract_1(self):
        ...

    @abstractmethod
    def abstract_2(self):
        pass

    @abc.abstractmethod
    def abstract_3(self):
        ...

    def body_1(self):
        print("foo")
        ...

    def body_2(self):
        self.body_1()


class NonAbstractClass:
    def empty_1(self):  # safe
        ...

    def empty_2(self):  # safe
        pass
