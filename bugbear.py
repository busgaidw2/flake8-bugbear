import ast
from collections import namedtuple
from functools import partial

import attr
import pep8


__version__ = '16.4.2'


@attr.s
class BugBearChecker(object):
    name = 'flake8-bugbear'
    version = __version__

    tree = attr.ib(default=None)
    filename = attr.ib(default='(none)')
    builtins = attr.ib(default=None)
    lines = attr.ib(default=None)
    visitor = attr.ib(default=attr.Factory(lambda: BugBearVisitor))

    def run(self):
        if not self.tree or not self.lines:
            self.load_file()
        visitor = self.visitor(
            filename=self.filename,
            lines=self.lines,
        )
        visitor.visit(self.tree)
        for e in visitor.errors:
            if pep8.noqa(self.lines[e.lineno - 1]):
                continue

            yield e

    def load_file(self):
        """Loads the file in a way that auto-detects source encoding and deals
        with broken terminal encodings for stdin.

        Stolen from flake8_import_order because it's good.
        """

        if self.filename in ("stdin", "-", None):
            self.filename = "stdin"
            self.lines = pep8.stdin_get_value().splitlines(True)
        else:
            self.lines = pep8.readlines(self.filename)

        if not self.tree:
            self.tree = ast.parse("".join(self.lines))


@attr.s
class BugBearVisitor(ast.NodeVisitor):
    filename = attr.ib()
    lines = attr.ib()
    node_stack = attr.ib(default=attr.Factory(list))
    errors = attr.ib(default=attr.Factory(list))
    futures = attr.ib(default=attr.Factory(set))

    if False:
        # Useful for tracing what the hell is going on.

        def __getattr__(self, name):
            print(name)
            return self.__getattribute__(name)

    def visit(self, node):
        self.node_stack.append(node)
        super().visit(node)
        self.node_stack.pop()

    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.errors.append(
                B001(node.lineno, node.col_offset)
            )
        self.generic_visit(node)


error = namedtuple('error', 'lineno col message type')
B001 = partial(
    error,
    message="B001: Do not use bare `except:`, it also catches unexpected "
            "events like memory errors, interrupts, system exit, and so on.  "
            "Prefer `except Exception:`.  If you're sure what you're doing, "
            "be explicit and write `except BaseException:`.",
    type=BugBearChecker,
)
