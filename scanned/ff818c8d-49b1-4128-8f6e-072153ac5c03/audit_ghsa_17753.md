# [H] try/except* clauses could allow bypass RestrictedPython via type confusion bug in the CPython interpreter

## Summary
Severity: High
Advisory: GHSA-gmj9-h825-chq2
CVE: CVE-2025-22153
CWE: CWE-843
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-01-23
Source: https://github.com/advisories/GHSA-gmj9-h825-chq2
Type: github-advisory

## Affected
- PyPI: `RestrictedPython` — affected >=6.0 <8.0

## Details
### Impact
Via a type confusion bug in the CPython interpreter when using `try/except*` RestrictedPython could be bypassed.

We believe this should be fixed upstream in Python itself until that we remove support for `try/except*` from RestrictedPython.
(It has been fixed for some Python versions.)

### Patches
Patched in version 8.0 by removing support for `try/except*` clauses

### Workarounds
There is no workaround.

### References
none

## References
- https://github.com/zopefoundation/RestrictedPython/security/advisories/GHSA-gmj9-h825-chq2
- https://nvd.nist.gov/vuln/detail/CVE-2025-22153
- https://github.com/zopefoundation/RestrictedPython/commit/48a92c5bb617a647cffd0dadd4d5cfe626bcdb2f
- https://github.com/zopefoundation/RestrictedPython
