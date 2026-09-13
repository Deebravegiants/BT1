# [M] pypdf: Missing stream length values ignore defined limits

## Summary
Severity: Medium
Advisory: GHSA-jm82-fx9c-mx94
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-jm82-fx9c-mx94
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.13.3

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to large memory usage, as `MAX_DECLARED_STREAM_LENGTH` is sometimes ignored. This requires parsing a content stream without a `/Length` value.

### Patches
This has been fixed in [pypdf==6.13.3](https://github.com/py-pdf/pypdf/releases/tag/6.13.3).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3871](https://github.com/py-pdf/pypdf/pull/3871).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-jm82-fx9c-mx94
- https://github.com/py-pdf/pypdf/pull/3871
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.13.3
