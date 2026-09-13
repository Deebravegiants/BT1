# [M] pypdf: Manipulated XMP metadata streams can exhaust RAM

## Summary
Severity: Medium
Advisory: GHSA-wjqc-6w8f-h24c
CVE: CVE-2026-48735
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-wjqc-6w8f-h24c
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.12.1

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to large memory usage. This requires parsing large XMP metadata, possibly with lots of unnecessary elements.

### Patches
This has been fixed in [pypdf==6.12.1](https://github.com/py-pdf/pypdf/releases/tag/6.12.1).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3796](https://github.com/py-pdf/pypdf/pull/3796).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-wjqc-6w8f-h24c
- https://nvd.nist.gov/vuln/detail/CVE-2026-48735
- https://github.com/py-pdf/pypdf/pull/3796
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.12.1
