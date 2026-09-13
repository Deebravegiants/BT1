# [H] Fickling has Code Injection vulnerability via pty.spawn()

## Summary
Severity: High
Advisory: GHSA-r7v6-mfhq-g3m2
CVE: CVE-2025-67748
CWE: CWE-184, CWE-502, CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-r7v6-mfhq-g3m2
Type: github-advisory

## Affected
- PyPI: `fickling` — affected >=0 <0.1.6

## Details
## Fickling Assessment

Based on the test case provided in the original report below, this bypass was caused by `pty` missing from our block list of unsafe module imports (as previously documented in #108), rather than the unused variable heuristic. This led to unsafe pickles based on `pty.spawn()` being incorrectly flagged as `LIKELY_SAFE`, and was fixed in https://github.com/trailofbits/fickling/pull/187. 

## Original report

### Summary
An unsafe deserialization vulnerability in Fickling allows a crafted pickle file to bypass the "unused variable" heuristic, enabling arbitrary code execution. This bypass is achieved by adding a trivial operation to the pickle file that "uses" the otherwise unused variable left on the stack after a malicious operation, tricking the detection mechanism into classifying the file as safe.

### Details
Fickling relies on the heuristic of detecting unused variables in the VM's stack after execution. Opcodes like `REDUCE`, `OBJ`, and `INST`, which can be used for arbitrary code execution, leave a value on the stack that is often unused in malicious pickle files.
This vulnerability enables a bypass by modifying the pickle file to use this leftover variable. A simple way to achieve this is to add a `BUILD` opcode that, in effect, adds a `__setstate__` to the unused variable. This makes Fickling consider the variable "used," thus failing to flag the malicious file.

### PoC
The following is a disassembled view of a malicious pickle file that bypasses Fickling's "unused variable" detection:
```
    0: \x80 PROTO      4
    2: \x95 FRAME      26
   11: \x8c SHORT_BINUNICODE 'pty'
   16: \x94 MEMOIZE    (as 0)
   17: \x8c SHORT_BINUNICODE 'spawn'
   24: \x94 MEMOIZE    (as 1)
   25: \x93 STACK_GLOBAL
   26: \x94 MEMOIZE    (as 2)
   27: \x8c SHORT_BINUNICODE 'id'
   31: \x94 MEMOIZE    (as 3)
   32: \x85 TUPLE1
   33: \x94 MEMOIZE    (as 4)
   34: R   REDUCE
   35: \x94 MEMOIZE    (as 5)
   36: \x8c SHORT_BINUNICODE 'gottem'
   44: \x94 MEMOIZE    (as 6)
   45: b   BUILD
   46: .   STOP
 ```
 
Here, the additions to the original pickle file can see on lines 35, 36, 44 and 45.

When analyzing this modified file, Fickling fails to identify it as malicious and reports it as **"LIKELY_SAFE"** as seen here:
```
{
    "severity": "LIKELY_SAFE",
    "analysis": "Warning: Fickling failed to detect any overtly unsafe code,but the pickle file may still be unsafe.Do not unpickle this file if it is from an untrusted source!\n\n",
    "detailed_results": {}
}
```

### Impact
This allows an attacker to craft a malicious pickle file that can bypass fickling since it relies on the "unused variable" heuristic to flag pickle files as unsafe. A user who deserializes such a file, believing it to be safe, would inadvertently execute arbitrary code on their system. This impacts any user or system that uses Fickling to vet pickle files for security issues.

## References
- https://github.com/trailofbits/fickling/security/advisories/GHSA-r7v6-mfhq-g3m2
- https://nvd.nist.gov/vuln/detail/CVE-2025-67748
- https://github.com/trailofbits/fickling/pull/108
- https://github.com/trailofbits/fickling/pull/187
- https://github.com/pypa/advisory-database/tree/main/vulns/fickling/PYSEC-2025-113.yaml
- https://github.com/trailofbits/fickling
