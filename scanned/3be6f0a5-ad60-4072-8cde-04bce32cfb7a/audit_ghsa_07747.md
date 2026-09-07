# [M] pypdf has a possible infinite loop when processing TreeObject

## Summary
Severity: Medium
Advisory: GHSA-996q-pr4m-cvgq
CVE: CVE-2026-27024
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-996q-pr4m-cvgq
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.7.1

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop. This requires accessing the children of a `TreeObject`, for example as part of outlines.

### Patches

This has been fixed in [pypdf==6.7.1](https://github.com/py-pdf/pypdf/releases/tag/6.7.1).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3645](https://github.com/py-pdf/pypdf/pull/3645).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-996q-pr4m-cvgq
- https://nvd.nist.gov/vuln/detail/CVE-2026-27024
- https://github.com/py-pdf/pypdf/pull/3645
- https://github.com/py-pdf/pypdf/commit/bd2f6d052fe5941e85e37082c2a43453d48d1295
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.7.1
