# [H] Tryton Improper Access Control

## Summary
Severity: High
Advisory: GHSA-f6f2-pwrj-64h3
CVE: CVE-2019-10868
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-04-10
Source: https://github.com/advisories/GHSA-f6f2-pwrj-64h3
Type: github-advisory

## Affected
- PyPI: `trytond` — affected >=4.2.0 <4.2.21
- PyPI: `trytond` — affected >=4.4.0 <4.4.19
- PyPI: `trytond` — affected >=4.6.0 <4.6.14
- PyPI: `trytond` — affected >=4.8.0 <4.8.10
- PyPI: `trytond` — affected >=5.0.0 <5.0.6

## Details
In `trytond/model/modelstorage.py` in Tryton 4.2 before 4.2.21, 4.4 before 4.4.19, 4.6 before 4.6.14, 4.8 before 4.8.10, and 5.0 before 5.0.6, an authenticated user can order records based on a field for which he has no access right. This may allow the user to guess values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10868
- https://discuss.tryton.org/t/security-release-for-issue8189/1262
- https://github.com/pypa/advisory-database/tree/main/vulns/trytond/PYSEC-2019-127.yaml
- https://github.com/tryton/trytond
- https://hg.tryton.org/trytond/rev/f58bbfe0aefb
- https://seclists.org/bugtraq/2019/Apr/14
- https://www.debian.org/security/2019/dsa-4426
