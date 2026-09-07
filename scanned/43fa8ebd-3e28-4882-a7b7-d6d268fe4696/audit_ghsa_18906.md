# [M] Tryton sao allows XSS via an HTML attachment

## Summary
Severity: Medium
Advisory: GHSA-xhgv-99mj-8m2x
CVE: CVE-2025-66420
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-30
Source: https://github.com/advisories/GHSA-xhgv-99mj-8m2x
Type: github-advisory

## Affected
- npm: `tryton-sao` — affected >=7.5.0 <7.6.9
- npm: `tryton-sao` — affected >=7.1.0 <7.4.19
- npm: `tryton-sao` — affected >=7.0.0 <7.0.38
- npm: `tryton-sao` — affected >=0 <6.0.67

## Details
Tryton sao (aka tryton-sao) before 7.6.9 allows XSS via an HTML attachment. This is fixed in 7.6.9, 7.4.19, 7.0.38, and 6.0.67.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66420
- https://discuss.tryton.org/t/security-release-for-issue-14290/8895
- https://foss.heptapod.net/tryton/tryton/-/issues/14290
- https://github.com/tryton/sao
