# [M] trytond arbitrary fields write via a sequence of records

## Summary
Severity: Medium
Advisory: GHSA-c8q5-2j73-qvcc
CVE: CVE-2015-0861
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-c8q5-2j73-qvcc
Type: github-advisory

## Affected
- PyPI: `trytond` — affected >=3.2.0 <3.2.10
- PyPI: `trytond` — affected >=3.4.0 <3.4.8
- PyPI: `trytond` — affected >=3.6.0 <3.6.5
- PyPI: `trytond` — affected >=3.8.0 <3.8.1

## Details
`model/modelstorage.py` in trytond 3.2.x before 3.2.10, 3.4.x before 3.4.8, 3.6.x before 3.6.5, and 3.8.x before 3.8.1 allows remote authenticated users to bypass intended access restrictions and write to arbitrary fields via a sequence of records.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0861
- https://bugs.tryton.org/issue5167
- https://foss.heptapod.net/tryton/tryton/-/commit/06230c381593c79766c4d8dcc92da3391e3acad2
- https://github.com/pypa/advisory-database/tree/main/vulns/trytond/PYSEC-2016-11.yaml
- https://github.com/tryton/trytond
- http://www.debian.org/security/2015/dsa-3425
- http://www.tryton.org/posts/security-release-for-issue5167.html
