==============
flake8-bugbear
==============

A plugin for flake8 finding likely bugs and design problems in your
program.  Contains warnings that don't belong in pyflakes and pep8::

    bug·bear  (bŭg′bâr′)
    n.
    1. A cause of fear, anxiety, or irritation: *Overcrowding is often
       a bugbear for train commuters.*
    2. A difficult or persistent problem: *"One of the major bugbears of
       traditional AI is the difficulty of programming computers to
       recognize that different but similar objects are instances of the
       same type of thing" (Jack Copeland).*
    3. A fearsome imaginary creature, especially one evoked to frighten
       children.

List of warnings
----------------

B001
~~~~

Do not use bare ``except:``, it also catches unexpected events " "like
memory errors, interrupts, system exit, and so on.  Prefer ``except
Exception:``.  If you're sure what you're doing, be explicit and write
``except BaseException:``.

Tests
-----

Just run::

    python setup.py test


License
-------

MIT


Change Log
----------

16.4.0
~~~~~~

* first published version

* date-versioned


Authors
-------

Glued together by `Łukasz Langa <mailto:lukasz@langa.pl>`_.
