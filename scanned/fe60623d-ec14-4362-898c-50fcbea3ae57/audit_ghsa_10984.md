# [M] pypdf has inefficient decoding of array-based streams

## Summary
Severity: Medium
Advisory: GHSA-qpxp-75px-xjcp
CVE: CVE-2026-33123
CWE: CWE-400, CWE-407
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-qpxp-75px-xjcp
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.9.1

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to long runtimes and/or large memory usage. This requires accessing an array-based stream with lots of entries.

### Patches
This has been fixed in [pypdf==6.9.1](https://github.com/py-pdf/pypdf/releases/tag/6.9.1).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3686](https://github.com/py-pdf/pypdf/pull/3686).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-qpxp-75px-xjcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33123
- https://github.com/py-pdf/pypdf/pull/3686
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.9.1
