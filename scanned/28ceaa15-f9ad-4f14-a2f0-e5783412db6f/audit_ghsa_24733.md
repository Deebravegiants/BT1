# [H] Plone SQL Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-hhmf-7rgg-gcw5
CVE: CVE-2020-7939
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hhmf-7rgg-gcw5
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=4.0

## Details
SQL Injection in DTML or in connection objects in Plone 4.0 through 5.2.1 allows users to perform unwanted SQL queries. (This is a problem in Zope.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7939
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2020-88.yaml
- https://plone.org/security/hotfix/20200121
- https://plone.org/security/hotfix/20200121/sql-injection-in-dtml-or-in-connection-objects
- https://www.openwall.com/lists/oss-security/2020/01/22/1
- http://www.openwall.com/lists/oss-security/2020/01/24/1
