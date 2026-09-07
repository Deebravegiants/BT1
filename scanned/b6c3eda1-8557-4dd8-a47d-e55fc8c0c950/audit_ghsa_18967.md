# [M] Tryton sao allows XSS because it does not escape completion values

## Summary
Severity: Medium
Advisory: GHSA-6qj9-2g9m-29x9
CVE: CVE-2025-66421
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-30
Source: https://github.com/advisories/GHSA-6qj9-2g9m-29x9
Type: github-advisory

## Affected
- npm: `tryton-sao` — affected >=7.5.0 <7.6.11
- npm: `tryton-sao` — affected >=7.1.0 <7.4.21
- npm: `tryton-sao` — affected >=7.0.0 <7.0.40
- npm: `tryton-sao` — affected >=0 <6.0.69

## Details
Tryton sao (aka tryton-sao) before 7.6.11 allows XSS because it does not escape completion values. This is fixed in 7.6.11, 7.4.21, 7.0.40, and 6.0.69.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66421
- https://discuss.tryton.org/t/security-release-for-issue-14363/8951
- https://foss.heptapod.net/tryton/tryton/-/issues/14363
- https://github.com/tryton/sao
