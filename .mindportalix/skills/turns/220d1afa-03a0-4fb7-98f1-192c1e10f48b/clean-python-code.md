---
name: clean-python-code
description: >
  Use this skill whenever writing, reviewing, or refactoring Python code —
  scripts, modules, functions, classes, or full applications — where code
  quality, readability, and maintainability matter, not just correctness.
  Triggers include: any request to "write clean code", "refactor this",
  "review my Python", "make this more Pythonic", "improve code quality",
  writing new .py files of non-trivial size (roughly >20 lines), or any
  Python code destined to be read/maintained by others (libraries, services,
  CLI tools, production scripts). Also apply proactively any time you are
  about to write Python code, even if the user didn't explicitly ask for
  "clean code" — treat this as the default bar, not an opt-in.
  Do NOT use for one-off throwaway scripts explicitly marked as
  quick/disposable (e.g. "just a quick one-liner to check X"), for
  non-Python languages, or for pure data/config files (JSON/YAML/CSV)
  with no logic.
location: /skills/clean-python-code.md
---

# Clean Python Code

Apply these rules whenever producing or reviewing Python code. They are ordered
roughly by impact: naming and structure matter more than micro-formatting.

## 1. Naming

- Names should say **what**, not **how**. `active_users`, not `au` or `list1`.
- Functions are verbs (`calculate_total`, `send_email`); variables are nouns
  (`total_price`, `user_list`); booleans read as yes/no questions
  (`is_valid`, `has_permission`, `should_retry`).
- Avoid abbreviations unless they're domain-standard (`id`, `url`, `db` are
  fine; `usr`, `calc`, `tmp_val` are not).
- Never shadow builtins (`list`, `dict`, `type`, `id`, `input`) as variable names.
- Constants are `UPPER_SNAKE_CASE` at module level.

**Before → After**
```python
# Before
def f(x, y):
    r = x * 0.9 if y else x
    return r

# After
def apply_discount(price: float, is_member: bool) -> float:
    MEMBER_DISCOUNT = 0.9
    return price * MEMBER_DISCOUNT if is_member else price
```

## 2. Functions

- One function, one responsibility. If you need "and" to describe what it
  does ("parses the file *and* writes to the DB"), split it.
- Keep functions short enough to see on one screen (~20-30 lines is a
  reasonable soft ceiling, not a hard rule — clarity trumps line count).
- Limit positional parameters to ~3-4; beyond that, use keyword-only
  arguments or a small dataclass/config object.
- Prefer early returns (guard clauses) over deep nesting.

**Before → After**
```python
# Before
def process(order):
    if order is not None:
        if order.items:
            if order.paid:
                ship(order)
            else:
                print("not paid")
        else:
            print("empty order")
    else:
        print("no order")

# After
def process(order: Order | None) -> None:
    if order is None:
        raise ValueError("order is required")
    if not order.items:
        raise ValueError("order has no items")
    if not order.paid:
        raise PaymentError("order is not paid")
    ship(order)
```

## 3. Type hints

- Add type hints to every function signature (params + return) in
  library/application code. This is the single highest-leverage clean-code
  habit in modern Python — it documents intent and enables static checking.
- Use `X | None` (3.10+) instead of `Optional[X]` unless targeting older
  Python; be consistent within a codebase.
- For collections, hint the contents: `list[str]`, not bare `list`.
- Don't over-hint trivial local variables where inference is obvious
  (`x: int = 5` is noise); do hint public function signatures and class
  attributes.

## 4. Errors and control flow

- Never use a bare `except:`. Catch specific exceptions.
- Don't use exceptions for expected, normal control flow (e.g. checking a
  key exists) when a simple check (`in`, `.get()`, `getattr` with default)
  reads more clearly — but DO use exceptions for genuinely exceptional or
  invalid states rather than sentinel return values like `-1` or `None`
  that the caller might forget to check.
- Fail fast: validate inputs at the top of a function rather than letting
  bad data silently propagate.
- Custom exceptions should subclass a meaningful base, not bare `Exception`,
  when a module defines more than one error type.

```python
# Avoid
try:
    value = data["key"]
except:
    value = None

# Prefer
value = data.get("key")
```

## 5. Structure and imports

- Standard library imports, then third-party, then local — each group
  alphabetized, separated by a blank line (this is what tools like `isort`
  enforce; follow it even without the tool).
- No wildcard imports (`from module import *`) outside of `__init__.py`
  re-export patterns.
- One class/major concept per module where reasonable; avoid 1000+ line
  "god files."
- Avoid circular imports by keeping dependency direction one-way; if two
  modules need each other, extract the shared piece into a third module.

## 6. Comments and docstrings

- Code should explain *what*; comments should explain *why* — don't
  restate the code in English.
- Every public function/class gets a docstring: one-line summary, then
  (if non-trivial) Args/Returns/Raises. Google or NumPy style, pick one
  and stay consistent within a project.
- Delete commented-out dead code rather than leaving it "just in case" —
  version control is the safety net, not comments.

```python
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance between two points in kilometers.

    Args:
        lat1, lon1: Coordinates of the first point, in decimal degrees.
        lat2, lon2: Coordinates of the second point, in decimal degrees.

    Returns:
        Distance in kilometers.
    """
```

## 7. Pythonic idioms

- Use comprehensions for simple transforms/filters; fall back to a loop
  once a comprehension needs more than one condition or nesting level —
  a comprehension that needs a comment to explain it has failed its job.
- Use `enumerate()` instead of manual index counters; use `zip()` instead
  of indexing two lists in parallel.
- Use context managers (`with open(...) as f:`) for anything with
  acquire/release semantics (files, locks, DB connections).
- Prefer `pathlib.Path` over raw string path manipulation.
- Use f-strings for formatting, not `%` or `.format()`, in new code.
- Use dataclasses (`@dataclass`) instead of plain classes that are just
  bags of attributes with an `__init__`.

```python
# Avoid
squares = []
for i in range(10):
    if i % 2 == 0:
        squares.append(i ** 2)

# Prefer
squares = [i ** 2 for i in range(10) if i % 2 == 0]
```

## 8. Testing hooks

- Design functions to be testable: pass dependencies in (params) rather
  than reaching out to globals/singletons inside the function body.
- Pure functions (same input → same output, no side effects) wherever
  the logic allows it — push I/O and side effects to the edges of the
  call graph, keep the core logic pure.

## 9. Formatting baseline

- Follow PEP 8; in practice, run `black` and `ruff`/`flake8` rather than
  hand-enforcing spacing — don't spend review time on things a formatter
  settles automatically.
- Line length: 88 (black default) or 79 (strict PEP 8) — pick one per
  project and don't mix.

## Anti-pattern checklist (scan for these before finishing)

- [ ] Bare `except:`
- [ ] Mutable default argument (`def f(x, items=[])`) — use `None` + create
      inside the function instead
- [ ] Deep nesting (>3 levels) that could be flattened with early returns
- [ ] Functions doing more than one thing (check the name for "and")
- [ ] Magic numbers/strings with no named constant
- [ ] Global mutable state modified from multiple functions
- [ ] Commented-out dead code left in
- [ ] Inconsistent naming style within the same file (mixing `camelCase`
      and `snake_case`)
- [ ] Missing type hints on public function signatures

## Worked example (full before/after)

```python
# Before
def calc(d):
    res = []
    for i in d:
        if i['status'] == 1:
            t = i['price'] * i['qty']
            if i['discount']:
                t = t * 0.9
            res.append(t)
    return sum(res)
```

```python
# After
from dataclasses import dataclass

ACTIVE_STATUS = 1
DISCOUNT_RATE = 0.9


@dataclass
class LineItem:
    status: int
    price: float
    quantity: int
    has_discount: bool


def calculate_order_total(items: list[LineItem]) -> float:
    """Sum the price of all active line items, applying discounts.

    Args:
        items: Line items to total.

    Returns:
        The total price across all active items.
    """
    active_items = (item for item in items if item.status == ACTIVE_STATUS)
    return sum(_line_total(item) for item in active_items)


def _line_total(item: LineItem) -> float:
    total = item.price * item.quantity
    return total * DISCOUNT_RATE if item.has_discount else total
```

What changed and why: named the magic `1` and `0.9`; replaced the dict
blob with a typed `LineItem` so the shape of the data is documented and
checkable; split the "which items count" logic from the "how do I total
one item" logic into two functions, each doing one thing; added a
docstring and full type hints; renamed everything to say what it means.
