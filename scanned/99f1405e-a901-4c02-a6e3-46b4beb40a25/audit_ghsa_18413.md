# [M] MaterialX Stack Overflow via Lack of MTLX XML Parsing Recursion Limit 

## Summary
Severity: Medium
Advisory: GHSA-wx6g-fm6f-w822
CVE: CVE-2025-53009
CWE: CWE-121
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-wx6g-fm6f-w822
Type: github-advisory

## Affected
- PyPI: `MaterialX` — affected >=1.39.2 <1.39.3

## Details
### Summary

When parsing an MTLX file with multiple nested `nodegraph` implementations, the MaterialX XML parsing logic can potentially crash due to stack exhaustion.

### Details

By specification, multiple kinds of elements in MTLX support nesting other elements, such as in the case of `nodegraph` elements. Parsing these subtrees is implemented via recursion, and since there is no max depth imposed on the XML document, this can lead to a stack overflow when the library parses an MTLX file with an excessively high number of nested elements.

### PoC

Please download the `recursion_overflow.mtlx` file from the following link: 

https://github.com/ShielderSec/poc/tree/main/CVE-2025-53009

`build/bin/MaterialXView --material recursion_overflow.mtlx`


### Impact
An attacker could intentionally crash a target program that uses MaterialX by sending a malicious MTLX file.

## References
- https://github.com/AcademySoftwareFoundation/MaterialX/security/advisories/GHSA-wx6g-fm6f-w822
- https://nvd.nist.gov/vuln/detail/CVE-2025-53009
- https://github.com/AcademySoftwareFoundation/MaterialX/issues/2504
- https://github.com/AcademySoftwareFoundation/MaterialX/pull/2505
- https://github.com/AcademySoftwareFoundation/MaterialX/commit/91ffea0de7bfe7bcd0c399b07f04fc48227055ff
- https://github.com/AcademySoftwareFoundation/MaterialX
- https://github.com/AcademySoftwareFoundation/MaterialX/releases/tag/v1.39.3
- https://github.com/ShielderSec/poc/tree/main/CVE-2025-53009
