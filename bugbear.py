import ast
from collections import namedtuple
from contextlib import suppress
from functools import partial

import attr
import pycodestyle


__version__ = '16.12.0'


@attr.s
class BugBearChecker:
    name = 'flake8-bugbear'
    version = __version__

    tree = attr.ib(default=None)
    filename = attr.ib(default='(none)')
    builtins = attr.ib(default=None)
    lines = attr.ib(default=None)
    max_line_length = attr.ib(default=79)
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
            if pycodestyle.noqa(self.lines[e.lineno - 1]):
                continue

            yield e
        for lineno, line in enumerate(self.lines, start=1):
            length = len(line) - 1
            if length > 1.1 * self.max_line_length:
                if pycodestyle.noqa(line):
                    continue

                yield B950(
                    lineno,
                    length,
                    message='B950: line too long ({} > {} characters)'.format(
                        length, self.max_line_length,
                    ),
                )

    def load_file(self):
        """Loads the file in a way that auto-detects source encoding and deals
        with broken terminal encodings for stdin.

        Stolen from flake8_import_order because it's good.
        """

        if self.filename in ("stdin", "-", None):
            self.filename = "stdin"
            self.lines = pycodestyle.stdin_get_value().splitlines(True)
        else:
            self.lines = pycodestyle.readlines(self.filename)

        if not self.tree:
            self.tree = ast.parse("".join(self.lines))

    @staticmethod
    def add_options(optmanager):
        """Informs flake8 to ignore B9xx by default."""
        optmanager.extend_default_ignore(disabled_by_default)


@attr.s
class BugBearVisitor(ast.NodeVisitor):
    filename = attr.ib()
    lines = attr.ib()
    node_stack = attr.ib(default=attr.Factory(list))
    node_window = attr.ib(default=attr.Factory(list))
    errors = attr.ib(default=attr.Factory(list))
    futures = attr.ib(default=attr.Factory(set))

    NODE_WINDOW_SIZE = 4

    if False:
        # Useful for tracing what the hell is going on.

        def __getattr__(self, name):
            print(name)
            return self.__getattribute__(name)

    def visit(self, node):
        self.node_stack.append(node)
        self.node_window.append(node)
        self.node_window = self.node_window[-self.NODE_WINDOW_SIZE:]
        super().visit(node)
        self.node_stack.pop()

    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.errors.append(
                B001(node.lineno, node.col_offset)
            )
        self.generic_visit(node)

    def visit_UAdd(self, node):
        trailing_nodes = list(map(type, self.node_window[-4:]))
        if trailing_nodes == [ast.UnaryOp, ast.UAdd, ast.UnaryOp, ast.UAdd]:
            originator = self.node_window[-4]
            self.errors.append(
                B002(originator.lineno, originator.col_offset)
            )
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            for bug in (B301, B302, B305):
                if node.func.attr in bug.methods:
                    call_path = '.'.join(self.compose_call_path(node.func.value))
                    if call_path not in bug.valid_paths:
                        self.errors.append(
                            bug(node.lineno, node.col_offset)
                        )
                    break
            else:
                self.check_for_b005(node)
        else:
            with suppress(AttributeError, IndexError):
                if (
                    node.func.id in ('getattr', 'hasattr') and
                    node.args[1].s == '__call__'
                ):
                    self.errors.append(
                        B004(node.lineno, node.col_offset)
                    )

        self.generic_visit(node)

    def visit_Attribute(self, node):
        call_path = list(self.compose_call_path(node))
        if '.'.join(call_path) == 'sys.maxint':
            self.errors.append(
                B304(node.lineno, node.col_offset)
            )
        elif len(call_path) == 2 and call_path[1] == 'message':
            name = call_path[0]
            for elem in reversed(self.node_stack[:-1]):
                if isinstance(elem, ast.ExceptHandler) and elem.name == name:
                    self.errors.append(
                        B306(node.lineno, node.col_offset)
                    )
                    break

    def visit_Assign(self, node):
        if isinstance(self.node_stack[-2], ast.ClassDef):
            # note: by hasattr belowe we're ignoring starred arguments, slices
            # and tuples for simplicity.
            assign_targets = {t.id for t in node.targets if hasattr(t, 'id')}
            if '__metaclass__' in assign_targets:
                self.errors.append(
                    B303(node.lineno, node.col_offset)
                )
        elif len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name):
                if (t.value.id, t.attr) == ('os', 'environ'):
                    self.errors.append(
                        B003(node.lineno, node.col_offset)
                    )
        self.generic_visit(node)

    def visit_For(self, node):
        if not node.target.id.startswith('_'):
            self.check_for_b007(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        xs = list(node.body)
        has_yield = False
        return_node = None
        while xs:
            x = xs.pop()
            if isinstance(x, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue
            elif isinstance(x, (ast.Yield, ast.YieldFrom)):
                has_yield = True
            elif isinstance(x, ast.Return) and x.value is not None:
                return_node = x

            if has_yield and return_node is not None:
                self.errors.append(
                    B901(return_node.lineno, return_node.col_offset)
                )
                break

            xs.extend(ast.iter_child_nodes(x))

        for default in node.args.defaults:
            if isinstance(default, B006.mutable_literals):
                self.errors.append(
                    B006(default.lineno, default.col_offset)
                )
            elif isinstance(default, ast.Call):
                call_path = '.'.join(self.compose_call_path(default.func))
                if call_path in B006.mutable_calls:
                    self.errors.append(
                        B006(default.lineno, default.col_offset)
                    )

        self.generic_visit(node)

    def compose_call_path(self, node):
        if isinstance(node, ast.Attribute):
            yield from self.compose_call_path(node.value)
            yield node.attr
        elif isinstance(node, ast.Name):
            yield node.id

    def check_for_b005(self, node):
        if node.func.attr not in B005.methods:
            return  # method name doesn't match

        if len(node.args) != 1 or not isinstance(node.args[0], ast.Str):
            return  # used arguments don't match the builtin strip

        call_path = '.'.join(self.compose_call_path(node.func.value))
        if call_path in B005.valid_paths:
            return  # path is exempt

        s = node.args[0].s
        if len(s) == 1:
            return  # stripping just one character

        if len(s) == len(set(s)):
            return  # no characters appear more than once

        self.errors.append(
            B005(node.lineno, node.col_offset)
        )

    def check_for_b007(self, node):
        target = node.target
        finder = NameFinder(name=target.id)
        for expr in node.body:
            finder.visit(expr)
            if finder.found:
                break

        if not finder.found:
            self.errors.append(
                B007(target.lineno, target.col_offset)
            )


@attr.s
class NameFinder(ast.NodeVisitor):
    """Finds a name within a tree of nodes.

    After `.visit(node)` is called, sets `found` to True if `name` is present in
    `node` or its children.
    """
    name = attr.ib()
    found = attr.ib(default=False)

    def visit_Name(self, node):
        if node.id == self.name:
            self.found = True

    def generic_visit(self, node):
        """Small optimization to not continue visiting after name was found."""
        if self.found:
            return

        super().generic_visit(node)


error = namedtuple('error', 'lineno col message type')

B001 = partial(
    error,
    message="B001 Do not use bare `except:`, it also catches unexpected "
            "events like memory errors, interrupts, system exit, and so on.  "
            "Prefer `except Exception:`.  If you're sure what you're doing, "
            "be explicit and write `except BaseException:`.",
    type=BugBearChecker,
)

B002 = partial(
    error,
    message="B002 Python does not support the unary prefix increment. Writing "
            "++n is equivalent to +(+(n)), which equals n. You meant n += 1.",
    type=BugBearChecker,
)

B003 = partial(
    error,
    message="B003 Assigning to `os.environ` doesn't clear the environment. "
            "Subprocesses are going to see outdated variables, in disagreement "
            "with the current process. Use `os.environ.clear()` or the `env=` "
            "argument to Popen.",
    type=BugBearChecker,
)

B004 = partial(
    error,
    message="B004 Using `hasattr(x, '__call__')` to test if `x` is callable "
            "is unreliable. If `x` implements custom `__getattr__` or its "
            "`__call__` is itself not callable, you might get misleading "
            "results. Use `callable(x)` for consistent results.",
    type=BugBearChecker,
)

B005 = partial(
    error,
    message="B005 Using .strip() with multi-character strings is misleading "
            "the reader. It looks like stripping a substring. Move your "
            "character set to a constant if this is deliberate. Use "
            ".replace() or regular expressions to remove string fragments.",
    type=BugBearChecker,
)
B005.methods = {'lstrip', 'rstrip', 'strip'}
B005.valid_paths = {}

B006 = partial(
    error,
    message="B006 Do not use mutable data structures for argument defaults. "
            "All calls reuse one instance of that data structure, persisting "
            "changes between them.",
    type=BugBearChecker,
)
B006.mutable_literals = (ast.Dict, ast.List, ast.Set)
B006.mutable_calls = {
    'Counter',
    'OrderedDict',
    'collections.Counter',
    'collections.OrderedDict',
    'collections.defaultdict',
    'collections.deque',
    'defaultdict',
    'deque',
    'dict',
    'list',
    'set',
}
B007 = partial(
    error,
    message="B007 Loop control variable not used within the loop body. "
            "If this is intended, start the name with an underscore.",
    type=BugBearChecker,
)


# Those could be false positives but it's more dangerous to let them slip
# through if they're not.
B301 = partial(
    error,
    message="B301 Python 3 does not include `.iter*` methods on dictionaries. "
            "Remove the `iter` prefix from the method name. For Python 2 "
            "compatibility, prefer the Python 3 equivalent unless you expect "
            "the size of the container to be large or unbounded. Then use "
            "`six.iter*` or `future.utils.iter*`.",
    type=BugBearChecker,
)
B301.methods = {'iterkeys', 'itervalues', 'iteritems', 'iterlists'}
B301.valid_paths = {'six', 'future.utils', 'builtins'}

B302 = partial(
    error,
    message="B302 Python 3 does not include `.view*` methods on dictionaries. "
            "Remove the `view` prefix from the method name. For Python 2 "
            "compatibility, prefer the Python 3 equivalent unless you expect "
            "the size of the container to be large or unbounded. Then use "
            "`six.view*` or `future.utils.view*`.",
    type=BugBearChecker,
)
B302.methods = {'viewkeys', 'viewvalues', 'viewitems', 'viewlists'}
B302.valid_paths = {'six', 'future.utils', 'builtins'}

B303 = partial(
    error,
    message="B303 `__metaclass__` does nothing on Python 3. Use "
            "`class MyClass(BaseClass, metaclass=...)`. For Python 2 "
            "compatibility, use `six.add_metaclass`.",
    type=BugBearChecker,
)

B304 = partial(
    error,
    message="B304 `sys.maxint` is not a thing on Python 3. Use `sys.maxsize`.",
    type=BugBearChecker,
)

B305 = partial(
    error,
    message="B305 `.next()` is not a thing on Python 3. Use the `next()` "
            "builtin. For Python 2 compatibility, use `six.next()`.",
    type=BugBearChecker,
)
B305.methods = {'next'}
B305.valid_paths = {'six', 'future.utils', 'builtins'}

B306 = partial(
    error,
    message="B306 `BaseException.message` has been deprecated as of Python "
            "2.6 and is removed in Python 3. Use `str(e)` to access the "
            "user-readable message. Use `e.args` to access arguments passed "
            "to the exception.",
    type=BugBearChecker,
)

B901 = partial(
    error,
    message=("B901 Using `yield` together with `return x`. Use native "
             "`async def` coroutines or put a `# noqa` comment on this "
             "line if this was intentional."),
    type=BugBearChecker,
)
B950 = partial(
    error,
    message=("B950 line too long"),
    type=BugBearChecker,
)

disabled_by_default = ["B901", "B950"]
