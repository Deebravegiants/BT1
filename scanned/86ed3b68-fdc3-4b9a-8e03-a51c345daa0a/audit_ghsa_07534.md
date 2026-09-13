# [M] pypdf: Possible large memory usage for wrong image dimensions

## Summary
Severity: Medium
Advisory: GHSA-5qjq-93h5-hrgp
CVE: CVE-2026-59938
CWE: CWE-789
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-5qjq-93h5-hrgp
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.14.0

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to large memory usage. This requires loading images where the declared size values are much too large compared to the actual data.

### Patches

This has been fixed in [pypdf==6.14.0](https://github.com/py-pdf/pypdf/releases/tag/6.14.0).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3888](https://github.com/py-pdf/pypdf/pull/3888).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-5qjq-93h5-hrgp
- https://nvd.nist.gov/vuln/detail/CVE-2026-59938
- https://github.com/py-pdf/pypdf/pull/3888
- https://github.com/py-pdf/pypdf/commit/c64583be16b8e8763d8777075f8ecbf382014b7a
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.14.0
