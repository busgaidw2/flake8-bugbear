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

Do not use bare ``except:``, it also catches unexpected events like
memory errors, interrupts, system exit, and so on.  Prefer ``except
Exception:``.  If you're sure what you're doing, be explicit and write
``except BaseException:``.

Tests
-----

Just run::

    python setup.py test


OMG, this is Python 3 only!
---------------------------

Relax, you can run ``flake8`` with all popular plugins as a *tool*
perfectly fine under Python 3.5+ even if you want to analyze Python 2
code.  This way you'll be able to parse all of the new syntax supported
on Python 3 but also *effectively all* the Python 2 syntax at the same
time.

If you're still invested in Python 2, there might be a small subset of
deprecated syntax that you'd have to abandon... but you're already doing
that, right?  `six <https://pypi.python.org/pypi/six>`_ or
`python-future <https://pypi.python.org/pypi/future>`_ bridge the gaps.

By making the code exclusively Python 3.5+, I'm able to focus on the
quality of the checks and re-use all the nice features of the new
releases (check out `pathlib <docs.python.org/3/library/pathlib.html>`_)
instead of wasting cycles on Unicode compatiblity, etc.

License
-------

MIT


Change Log
----------

16.4.2
~~~~~~

* packaging herp derp

16.4.1
~~~~~~

* bugfix: include tests in the source package (to make ``setup.py test``
  work for everyone)

* bugfix: explicitly open README.rst in UTF-8 in setup.py for systems
  with other default encodings

16.4.0
~~~~~~

* first published version

* date-versioned


Authors
-------

Glued together by `Łukasz Langa <mailto:lukasz@langa.pl>`_.
