# [M] pypdf: Possible infinite loop when retrieving fonts for layout-mode text extraction

## Summary
Severity: Medium
Advisory: GHSA-52x6-gq3r-vpf4
CVE: CVE-2026-54530
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-52x6-gq3r-vpf4
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.13.0

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop. This requires extracting the text in layout mode.

### Patches

This has been fixed in [pypdf==6.13.0](https://github.com/py-pdf/pypdf/releases/tag/6.13.0).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3830](https://github.com/py-pdf/pypdf/pull/3830).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-52x6-gq3r-vpf4
- https://github.com/py-pdf/pypdf/pull/3830
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.13.0
