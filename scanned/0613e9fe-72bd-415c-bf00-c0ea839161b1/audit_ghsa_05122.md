# [M] pypdf: Inefficient decoding of FlateDecode PNG predictor streams

## Summary
Severity: Medium
Advisory: GHSA-5hgr-hg42-57jg
CVE: CVE-2026-49460
CWE: CWE-407
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-5hgr-hg42-57jg
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.12.2

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to long runtimes. This requires accessing a stream which uses the `/FlateDecode` filter with a PNG predictor.

### Patches
This has been fixed in [pypdf==6.12.2](https://github.com/py-pdf/pypdf/releases/tag/6.12.2).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3806](https://github.com/py-pdf/pypdf/pull/3806).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-5hgr-hg42-57jg
- https://github.com/py-pdf/pypdf/pull/3806
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.12.2
