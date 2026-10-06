# DComp320 – Stack-Based Expression Evaluator

## Student Information

| Field | Details |
|---|---|
| **Name** | Christian Lalugba |
| **ID** | 905005435 |
| **Class** | DIT2101F |

---

**Course:** DComp320 – Data Structures and Algorithms
**Assignment:** Stack Implementation (Individual)
**University:** Limkokwing University of Creative Technology – Sierra Leone

## 1. Purpose

A Python program that reads mathematical expressions from `input.txt`,
evaluates each one using a **Stack** data structure (no `eval()`/`exec()`),
and writes the results to `output.txt` in the same layout as the input.

## 2. Requirements and Python version

- Python 3.8 or newer (developed and tested with **Python 3.12.3**)
- No external packages. Only the standard library modules `os` and `sys` are used.

## 3. Project structure

```
DComp320_Stack_Assignment/
├── main.py               Stack class, tokenizer, evaluator, file I/O, test runner
├── input.txt             Lecturer's sample input
├── output.txt            Generated results
├── README.md             This file
├── tests/
│   └── test_cases.txt    "expression | expected" test cases
└── screenshots/          For screenshots to be used in the report
```

## 4. How to run

```
python main.py                 # reads input.txt, writes output.txt
python main.py in.txt out.txt  # optional: custom file names
python main.py --test          # runs tests/test_cases.txt
```
(Use `python3` instead of `python` on systems where that is the command.)

## 5. Input file structure

- One expression per line.
- A line made only of three or more dashes (e.g. `----`) is a **separator**, not an expression.
- Blank lines are allowed and are preserved.

```
3 + 5 ** 2
----
(3 / 4) + 7 * 2
----
10 - (2 + 3) ** 4
```

## 6. Output file structure

One result per expression, on the same line position as the input, with each
separator copied unchanged. No labels such as "Result:" are written.
Whole numbers print without `.0` (`8`, not `8.0`); decimals stay decimal (`0.75`).

```
28
----
14.75
----
-615
```

## 7. Supported operators

| Operator | Meaning | Notes |
|---|---|---|
| `+` `-` | add, subtract | also unary sign, e.g. `-(3 + 2)` |
| `*` `/` | multiply, divide | `10 / 2` gives `5`, `3 / 4` gives `0.75` |
| `**` | exponentiation | required because the lecturer's sample uses it |
| `( )` | grouping | any nesting depth |

Numbers may be integers or decimals (`1.5`, `.5`).

## 8. Stack implementation

`class Stack` (in `main.py`) is a LIFO structure backed by a Python list:

| Method | Behaviour |
|---|---|
| `push(item)` | place item on top |
| `pop()` | remove and return the top item |
| `peek()` | return the top item without removing it |
| `is_empty()`, `size()` | helpers |

`pop()` and `peek()` on an empty stack raise `EmptyStackError` with a clear
message instead of an obscure list error.

## 9. Expression evaluation approach

The evaluator (`evaluate_expression`) uses **two Stack objects**
(the operator-precedence / shunting-yard idea):

1. `tokenize_expression` splits the text into numbers, operators and parentheses (`**` is read as one token).
2. **Value stack** holds numbers and intermediate results; **operator stack** holds operators and `(`.
3. Number → push on value stack.
4. `(` → push on operator stack.
5. `)` → pop and apply operators until the matching `(` is found, then discard `(`.
6. Operator → while the operator on top of the operator stack must be applied first (higher precedence, or equal precedence and left-associative), `apply_operator` pops two values, computes, and pushes the result. Then push the new operator.
7. At the end, apply all remaining operators. The single value left on the value stack is the answer.

`apply_operator` pops the right operand first, then the left, so `10 - 3` is computed correctly.

## 10. Operator precedence

Highest to lowest:

| Level | Operators | Associativity |
|---|---|---|
| 1 | `( )` | – (handled by the stack logic) |
| 2 | `**` | right (`2 ** 3 ** 2` = 512) |
| 3 | unary `-` / `+` | right (`-2 ** 2` = -4, as in standard maths) |
| 4 | `*` `/` | left |
| 5 | `+` `-` | left |

## 11. Testing

`python main.py --test` runs every line of `tests/test_cases.txt`
(format `expression | expected`; `ERROR` means the expression must be rejected)
plus a file-level check of the lecturer's complete sample, including separators.

Covered: addition, subtraction, multiplication, division, precedence,
parentheses, nested parentheses, `**`, decimals, mixed operators,
right-associative chained `**`, unary minus, chained subtraction/division,
whitespace handling, and error cases (division by zero, mismatched parentheses,
invalid character, missing operand/operator, malformed number, `0 ** -1`).

Last recorded run: **33 passed, 0 failed.**

## 12. Important note on the lecturer's sample output

The sample output in the assignment sheet (`13`, `17`, `-10`) does **not** match
the sample input under normal mathematics. The correct values are:

| Expression | Correct result | Lecturer's sample output |
|---|---|---|
| `3 + 5 ** 2` | **28** (3 + 25) | 13 |
| `(3 / 4) + 7 * 2` | **14.75** (0.75 + 14) | 17 |
| `10 - (2 + 3) ** 4` | **-615** (10 - 625) | -10 |

The program computes the mathematically correct values. The assignment's own
requirement list also states `3 + 5 ** 2` must give `28`. The sample output was
not copied or forced, since doing so would make the evaluator wrong.
The lecturer's sample output appears to be illustrative only.

## 13. Assumptions

- One expression per line. A separator is a line of 3+ dashes, copied to the output exactly as written.
- `**` is exponentiation (not Python-style `^`).
- Division with an exact result between integers prints as an integer (`10 / 2` → `5`); otherwise as a decimal.
- Unary minus/plus is allowed (`-5 + 2`, `2 ** -1`).
- Decimal results are rounded to 10 places for display to hide floating-point noise (`0.1 + 0.2` → `0.3`).

## 14. Limitations

- No implicit multiplication: `2(3)` is rejected; write `2 * 3`.
- No variables, functions (`sqrt`), `%`, `//` or `^`.
- Decimal arithmetic uses Python floats, so very long decimals are approximate.
- Exponents above 10000 in absolute value are rejected to stop the program hanging.
- Expressions spanning several lines are not supported.
- The test runner is a simple custom script, not a framework such as `unittest`/`pytest`.

## 15. Error handling

An invalid expression never stops the program. Its output line becomes
`Error: <reason>` and the remaining expressions are still processed:

| Problem | Output line |
|---|---|
| `5 / 0` | `Error: division by zero` |
| `(2 + 3` or `2 + 3)` | `Error: mismatched parentheses` |
| `3 $ 4` | `Error: invalid character '$'` |
| `3 + * 2` | `Error: unexpected operator '*'` |
| `3 +` | `Error: expression ends unexpectedly` |
| `2 3` | `Error: missing operator between values` |

A missing input file prints a message and exits with status 1.

## 16. GitHub

Repository: [https://github.com/christianlalugba/Data-structure-and-Algorithm-](https://github.com/christianlalugba/Data-structure-and-Algorithm-)

```
git remote add origin https://github.com/christianlalugba/Data-structure-and-Algorithm-.git
git push -u origin main
```
