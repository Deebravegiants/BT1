# [M] Tryton Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7cwg-2575-3546
CVE: CVE-2017-0360
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7cwg-2575-3546
Type: github-advisory

## Affected
- PyPI: `trytond` — affected >=3.0.0
- PyPI: `trytond` — affected >=3.2.0
- PyPI: `trytond` — affected >=3.4.0
- PyPI: `trytond` — affected >=3.6.0
- PyPI: `trytond` — affected >=3.8.0
- PyPI: `trytond` — affected >=4.0.0
- PyPI: `trytond` — affected >=4.2.0 <4.2.3

## Details
file_open in Tryton 3.x and 4.x through 4.2.2 allows remote authenticated users with certain permissions to read arbitrary files via a "same root name but with a suffix" attack. NOTE: This vulnerability exists because of an incomplete fix for CVE-2016-1242.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0360
- https://github.com/tryton/trytond/commit/30e978593733385db3144f8c583eeb4679575cf0
- https://github.com/tryton/trytond/commit/a67a7f03c30277515f530cad5950056171ed5bd1
- https://github.com/pypa/advisory-database/tree/main/vulns/trytond/PYSEC-2017-97.yaml
- https://github.com/tryton/trytond
- https://lists.debian.org/debian-security-announce/2017/msg00084.html
- http://hg.tryton.org/trytond?cmd=changeset;node=472510fdc6f8
- http://www.debian.org/security/2017/dsa-3826
