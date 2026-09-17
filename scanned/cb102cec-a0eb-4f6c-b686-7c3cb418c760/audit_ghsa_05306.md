# [M] pypdf: Possible large memory usage for large offsets for layout mode text

## Summary
Severity: Medium
Advisory: GHSA-cj93-chg6-vgv8
CVE: CVE-2026-48155
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-cj93-chg6-vgv8
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.12.0

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to large memory usage. This requires extracting text in layout mode with large character offsets.

### Patches

This has been fixed in [pypdf==6.12.0](https://github.com/py-pdf/pypdf/releases/tag/6.12.0).

### Workarounds

If developers are unable to immediately upgrade, they should consider applying the changes from PR [#3790](https://github.com/py-pdf/pypdf/pull/3790).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-cj93-chg6-vgv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-48155
- https://github.com/py-pdf/pypdf/pull/3790
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.12.0
