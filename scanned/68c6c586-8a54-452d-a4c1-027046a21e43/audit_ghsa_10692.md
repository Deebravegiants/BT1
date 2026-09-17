# [M] pypdf: Manipulated FlateDecode image dimensions can exhaust RAM

## Summary
Severity: Medium
Advisory: GHSA-x284-j5p8-9c5p
CVE: CVE-2026-41314
CWE: CWE-789
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-x284-j5p8-9c5p
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.10.2

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to the RAM being exhausted. This requires accessing an image using `/FlateDecode` with large size values.

### Patches
This has been fixed in [pypdf==6.10.2](https://github.com/py-pdf/pypdf/releases/tag/6.10.2).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3734](https://github.com/py-pdf/pypdf/pull/3734).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-x284-j5p8-9c5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-41314
- https://github.com/py-pdf/pypdf/pull/3734
- https://github.com/py-pdf/pypdf/commit/ac734dab4eef92bcce50d503949b4d9887d89f11
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.10.2
