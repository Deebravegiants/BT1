# [M] trytond allows remote attackers to obtain sensitive trace-back (server setup) information

## Summary
Severity: Medium
Advisory: GHSA-jqfc-9q34-prhg
CVE: CVE-2025-66422
CWE: CWE-402
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-30
Source: https://github.com/advisories/GHSA-jqfc-9q34-prhg
Type: github-advisory

## Affected
- PyPI: `trytond` — affected >=7.5.0 <7.6.11
- PyPI: `trytond` — affected >=7.1.0 <7.4.21
- PyPI: `trytond` — affected >=7.0.0 <7.0.40
- PyPI: `trytond` — affected >=0 <6.0.70

## Details
Tryton trytond before 7.6.11 allows remote attackers to obtain sensitive trace-back (server setup) information. This is fixed in 7.6.11, 7.4.21, 7.0.40, and 6.0.70.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66422
- https://discuss.tryton.org/t/security-release-for-issue-14354/8950
- https://foss.heptapod.net/tryton/tryton/-/issues/14354
- https://github.com/tryton/trytond
