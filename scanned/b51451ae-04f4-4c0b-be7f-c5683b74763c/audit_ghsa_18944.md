# [H] trytond does not enforce access rights for the route of the HTML editor.

## Summary
Severity: High
Advisory: GHSA-p3p5-xrmv-4j6x
CVE: CVE-2025-66423
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-11-30
Source: https://github.com/advisories/GHSA-p3p5-xrmv-4j6x
Type: github-advisory

## Affected
- PyPI: `trytond` — affected >=7.5.0 <7.6.11
- PyPI: `trytond` — affected >=7.1.0 <7.4.21
- PyPI: `trytond` — affected >=7.0.0 <7.0.40
- PyPI: `trytond` — affected >=6.0.0 <6.0.70

## Details
Tryton trytond 6.0 before 7.6.11 does not enforce access rights for the route of the HTML editor. This is fixed in 7.6.11, 7.4.21, 7.0.40, and 6.0.70.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66423
- https://discuss.tryton.org/t/security-release-for-issue-14364/8952
- https://foss.heptapod.net/tryton/tryton/-/issues/14364
- https://github.com/tryton/trytond
