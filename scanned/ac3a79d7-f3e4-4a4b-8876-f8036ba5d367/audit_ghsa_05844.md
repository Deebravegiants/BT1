# [M] pypdf: Possible large memory usage for large /ToUnicode streams

## Summary
Severity: Medium
Advisory: GHSA-fp3f-mc75-235c
CVE: CVE-2026-71870
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-fp3f-mc75-235c
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.15.0

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to large memory consumption. This requires parsing the `/ToUnicode` entry of a font with unusually large values, for example during text extraction.

### Patches

This has been fixed in [pypdf==6.15.0](https://github.com/py-pdf/pypdf/releases/tag/6.15.0).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3944](https://github.com/py-pdf/pypdf/pull/3944).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-fp3f-mc75-235c
- https://github.com/py-pdf/pypdf/pull/3944
- https://github.com/py-pdf/pypdf/commit/afba8080e19d29a3c256a742b340995e695b35aa
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.15.0
