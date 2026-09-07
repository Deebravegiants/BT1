# [H] ChangeDetection.io XSS in watch overview

## Summary
Severity: High
Advisory: GHSA-hwpg-x5hw-vpv9
CVE: CVE-2025-52558
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-23
Source: https://github.com/advisories/GHSA-hwpg-x5hw-vpv9
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.50.4

## Details
### Impact
XSS - Errors in filters from website page change detection watches were not being filtered.

### Patches

0.50.4

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-hwpg-x5hw-vpv9
- https://nvd.nist.gov/vuln/detail/CVE-2025-52558
- https://github.com/dgtlmoon/changedetection.io/commit/3d5a544ea674cfce517adcd498877a8d760d0931
- https://github.com/dgtlmoon/changedetection.io
