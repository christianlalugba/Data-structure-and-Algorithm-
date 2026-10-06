"""
DComp320 - Data Structures and Algorithms
Assignment: Stack Implementation (Individual)
Limkokwing University of Creative Technology - Sierra Leone

Reads mathematical expressions from input.txt, evaluates each one using a
stack-based algorithm (two stacks: operands and operators), and writes the
results to output.txt using the same separator layout as the input.

Python's eval()/exec() are NOT used anywhere in this program.

Usage:
    python main.py                      # input.txt -> output.txt
    python main.py in.txt out.txt       # custom file names
    python main.py --test               # run tests/test_cases.txt
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Safety limit so an expression like 9 ** 9 ** 9 cannot hang the program.
MAX_EXPONENT = 10000


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------
class ExpressionError(Exception):
    """Raised when an expression is invalid or cannot be evaluated."""


class EmptyStackError(IndexError):
    """Raised when pop() or peek() is called on an empty Stack."""


# ---------------------------------------------------------------------------
# Stack data structure (LIFO)
# ---------------------------------------------------------------------------
class Stack:
    """A simple Last-In-First-Out stack backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Place item on top of the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item. Raises EmptyStackError if empty."""
        if self.is_empty():
            raise EmptyStackError("pop from an empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it. Raises if empty."""
        if self.is_empty():
            raise EmptyStackError("peek at an empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------
def tokenize_expression(expression):
    """
    Convert a string into a list of (kind, value) tokens.
    kind is 'number', 'operator' or 'paren'.
    Numbers become int (e.g. 5) or float (e.g. 0.75).
    '**' is recognised as a single operator.
    """
    tokens = []
    i = 0
    length = len(expression)

    while i < length:
        ch = expression[i]

        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            start = i
            while i < length and (expression[i].isdigit() or expression[i] == "."):
                i += 1
            text = expression[start:i]
            if text.count(".") > 1 or text == ".":
                raise ExpressionError(f"invalid number '{text}'")
            tokens.append(("number", float(text) if "." in text else int(text)))
        elif ch == "*":
            if i + 1 < length and expression[i + 1] == "*":
                tokens.append(("operator", "**"))
                i += 2
            else:
                tokens.append(("operator", "*"))
                i += 1
        elif ch in "+-/":
            tokens.append(("operator", ch))
            i += 1
        elif ch in "()":
            tokens.append(("paren", ch))
            i += 1
        else:
            raise ExpressionError(f"invalid character '{ch}'")

    return tokens


# ---------------------------------------------------------------------------
# Operator rules
# ---------------------------------------------------------------------------
# Higher number = binds tighter. 'u-'/'u+' are unary minus/plus; they sit
# between * / and ** so that -2 ** 2 == -(2 ** 2) == -4 (same as Python/maths).
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "u-": 3, "u+": 3, "**": 4}
UNARY_OPERATORS = ("u-", "u+")


def precedence(operator):
    return PRECEDENCE[operator]


def is_right_associative(operator):
    """** is right-associative: 2 ** 3 ** 2 == 2 ** (3 ** 2) == 512."""
    return operator == "**"


def apply_operator(operator, values):
    """Pop the needed operand(s) from the value stack, compute, push result."""
    if operator in UNARY_OPERATORS:
        operand = values.pop()
        values.push(-operand if operator == "u-" else operand)
        return

    right = values.pop()   # the top of the stack is the RIGHT operand
    left = values.pop()

    if operator == "+":
        result = left + right
    elif operator == "-":
        result = left - right
    elif operator == "*":
        result = left * right
    elif operator == "/":
        if right == 0:
            raise ExpressionError("division by zero")
        # Keep exact integer results as int (10 / 2 -> 5), else float (3 / 4 -> 0.75)
        if isinstance(left, int) and isinstance(right, int) and left % right == 0:
            result = left // right
        else:
            result = left / right
    elif operator == "**":
        if abs(right) > MAX_EXPONENT:
            raise ExpressionError("exponent too large")
        try:
            result = left ** right
        except ZeroDivisionError:
            raise ExpressionError("division by zero (0 raised to a negative power)")
        except OverflowError:
            raise ExpressionError("result too large")
        if isinstance(result, complex):
            raise ExpressionError("result is not a real number")
    else:
        raise ExpressionError(f"invalid operator '{operator}'")

    values.push(result)


def _should_apply_before(top_operator, incoming_operator):
    """True if the operator on top of the stack must be applied first."""
    top_p = precedence(top_operator)
    incoming_p = precedence(incoming_operator)
    if top_p > incoming_p:
        return True
    return top_p == incoming_p and not is_right_associative(incoming_operator)


# ---------------------------------------------------------------------------
# Evaluator (two stacks: values and operators)
# ---------------------------------------------------------------------------
def evaluate_expression(expression):
    """Evaluate an arithmetic expression string using two Stack objects."""
    tokens = tokenize_expression(expression)
    if not tokens:
        raise ExpressionError("empty expression")

    values = Stack()      # operands / intermediate results
    operators = Stack()   # operators and '(' markers
    expect_operand = True  # True when the next token must start an operand

    try:
        for kind, value in tokens:
            if kind == "number":
                if not expect_operand:
                    raise ExpressionError("missing operator between values")
                values.push(value)
                expect_operand = False

            elif value == "(":
                if not expect_operand:
                    raise ExpressionError("missing operator before '('")
                operators.push("(")

            elif value == ")":
                if expect_operand:
                    raise ExpressionError("unexpected ')'")
                while not operators.is_empty() and operators.peek() != "(":
                    apply_operator(operators.pop(), values)
                if operators.is_empty():
                    raise ExpressionError("mismatched parentheses")
                operators.pop()  # discard the '('

            else:  # operator
                if expect_operand:
                    # In operand position only + and - are allowed (unary sign)
                    if value in ("+", "-"):
                        operators.push("u" + value)
                        continue
                    raise ExpressionError(f"unexpected operator '{value}'")
                while (not operators.is_empty()
                       and operators.peek() != "("
                       and _should_apply_before(operators.peek(), value)):
                    apply_operator(operators.pop(), values)
                operators.push(value)
                expect_operand = True

        if expect_operand:
            raise ExpressionError("expression ends unexpectedly")

        while not operators.is_empty():
            operator = operators.pop()
            if operator == "(":
                raise ExpressionError("mismatched parentheses")
            apply_operator(operator, values)

        result = values.pop()
        if not values.is_empty():
            raise ExpressionError("malformed expression")
        return result

    except EmptyStackError:
        raise ExpressionError("malformed expression")


# ---------------------------------------------------------------------------
# Formatting and file handling
# ---------------------------------------------------------------------------
def format_result(number):
    """8.0 -> '8', 0.75 -> '0.75', 0.1+0.2 -> '0.3'."""
    if isinstance(number, float):
        if number.is_integer() and abs(number) < 1e15:
            return str(int(number))
        return repr(round(number, 10))
    return str(number)


def is_separator(line):
    """A separator is a line made only of 3 or more '-' characters."""
    stripped = line.strip()
    return len(stripped) >= 3 and set(stripped) == {"-"}


def process_lines(lines):
    """Turn input lines into output lines (separators and blanks preserved)."""
    output_lines = []
    for line in lines:
        text = line.rstrip("\r\n")
        if is_separator(text):
            output_lines.append(text.strip())
        elif text.strip() == "":
            output_lines.append("")
        else:
            try:
                output_lines.append(format_result(evaluate_expression(text)))
            except ExpressionError as error:
                output_lines.append(f"Error: {error}")
    return output_lines


def read_input_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read().splitlines()


def write_output_file(path, output_lines):
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(output_lines) + "\n")


# ---------------------------------------------------------------------------
# Test runner  (python main.py --test)
# ---------------------------------------------------------------------------
def run_tests(test_file):
    """
    tests/test_cases.txt lines have the form:   expression | expected
    Lines starting with '#' are comments. Expected 'ERROR' means the
    expression must be rejected.
    """
    passed = failed = 0
    with open(test_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            expression, expected = [part.strip() for part in line.rsplit("|", 1)]
            try:
                actual = format_result(evaluate_expression(expression))
            except ExpressionError:
                actual = "ERROR"
            ok = actual == expected
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
            print(f"[{'PASS' if ok else 'FAIL'}] {expression!r:35} expected {expected!r:12} got {actual!r}")

    # Whole-file test using the lecturer's sample input
    sample_in = ["3 + 5 ** 2", "----", "(3 / 4) + 7 * 2", "----", "10 - (2 + 3) ** 4"]
    sample_out = ["28", "----", "14.75", "----", "-615"]
    ok = process_lines(sample_in) == sample_out
    passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
    print(f"[{'PASS' if ok else 'FAIL'}] lecturer's complete sample input (file-level, separators kept)")

    print(f"\n{passed} passed, {failed} failed, {passed + failed} total")
    return failed == 0


def main():
    args = sys.argv[1:]
    if args and args[0] == "--test":
        success = run_tests(os.path.join(BASE_DIR, "tests", "test_cases.txt"))
        sys.exit(0 if success else 1)

    input_path = args[0] if len(args) > 0 else os.path.join(BASE_DIR, "input.txt")
    output_path = args[1] if len(args) > 1 else os.path.join(BASE_DIR, "output.txt")

    try:
        lines = read_input_file(input_path)
    except OSError as error:
        print(f"Cannot read input file: {error}")
        sys.exit(1)

    write_output_file(output_path, process_lines(lines))
    print(f"Done. Results written to {output_path}")


if __name__ == "__main__":
    main()
