# [M] Aim Improper Access Control

## Summary
Severity: Medium
Advisory: GHSA-r229-5wgf-f28g
CVE: CVE-2024-8238
CWE: CWE-1336, CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-r229-5wgf-f28g
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=3.0.0

## Details
In version 3.22.0 of aimhubio/aim, the AimQL query language uses an outdated version of the safer_getattr() function from RestrictedPython. This version does not protect against the str.format_map() method, allowing an attacker to leak server-side secrets or potentially gain unrestricted code execution. The vulnerability arises because str.format_map() can read arbitrary attributes of Python objects, enabling attackers to access sensitive variables such as os.environ. If an attacker can write files to a known location on the Aim server, they can use str.format_map() to load a malicious .dll/.so file into the Python interpreter, leading to unrestricted code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8238
- https://github.com/aimhubio/aim
- https://github.com/aimhubio/aim/blob/main/aim/storage/query.py#L45
- https://huntr.com/bounties/4e140ef9-f6d1-4e68-a44c-3b9e856924d3
