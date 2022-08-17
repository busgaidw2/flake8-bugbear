import abc
import abc as notabc
from abc import ABC, ABCMeta
from abc import abstractmethod
from abc import abstractmethod as abstract
from abc import abstractmethod as abstractaoeuaoeuaoeu
from abc import abstractmethod as notabstract

import foo

"""
Should emit:
B024 - on lines 17, 34, 52, 58, 69, 74, 84, 89
"""


class Base_1(ABC):  # error
    def method(self):
        ...


class Base_2(ABC):
    @abstractmethod
    def method(self):
        ...


class Base_3(ABC):
    @abc.abstractmethod
    def method(self):
        ...


class Base_4(ABC):
    @notabc.abstractmethod
    def method(self):
        ...


class Base_5(ABC):
    @abstract
    def method(self):
        ...


class Base_6(ABC):
    @abstractaoeuaoeuaoeu
    def method(self):
        ...


class Base_7(ABC):  # error
    @notabstract
    def method(self):
        ...


class MetaBase_1(metaclass=ABCMeta):  # error
    def method(self):
        ...


class MetaBase_2(metaclass=ABCMeta):
    @abstractmethod
    def method(self):
        ...


class abc_Base_1(abc.ABC):  # error
    def method(self):
        ...


class abc_Base_2(metaclass=abc.ABCMeta):  # error
    def method(self):
        ...


class notabc_Base_1(notabc.ABC):  # safe
    def method(self):
        ...


class multi_super_1(notabc.ABC, abc.ABCMeta):  # error
    def method(self):
        ...


class multi_super_2(notabc.ABC, metaclass=abc.ABCMeta):  # error
    def method(self):
        ...
