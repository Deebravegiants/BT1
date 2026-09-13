# [M] Tryton allow authenticated users with certain permissions to read arbitrary files via the name parameter

## Summary
Severity: Medium
Advisory: GHSA-jpr7-8rxm-4vgx
CVE: CVE-2016-1242
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jpr7-8rxm-4vgx
Type: github-advisory

## Affected
- PyPI: `trytond` — affected >=0 <3.2.17
- PyPI: `trytond` — affected >=3.4 <3.4.14
- PyPI: `trytond` — affected >=3.6 <3.6.12
- PyPI: `trytond` — affected >=3.8 <3.8.8
- PyPI: `trytond` — affected >=4.0 <4.0.4

## Details
`file_open` in Tryton before 3.2.17, 3.4.x before 3.4.14, 3.6.x before 3.6.12, 3.8.x before 3.8.8, and 4.x before 4.0.4 allows remote authenticated users with certain permissions to read arbitrary files via the name parameter or unspecified other vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1242
- https://bugs.tryton.org/issue5808
- https://github.com/pypa/advisory-database/tree/main/vulns/tryton/PYSEC-2016-41.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/trytond/PYSEC-2016-13.yaml
- https://github.com/tryton/trytond
- http://www.debian.org/security/2016/dsa-3656
- http://www.tryton.org/posts/security-release-for-issue5795-and-issue5808.html
