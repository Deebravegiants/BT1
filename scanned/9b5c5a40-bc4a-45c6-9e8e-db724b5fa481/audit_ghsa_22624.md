# [C] Plone Unauthenticated Write Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-w6g9-xccc-347h
CVE: CVE-2020-7941
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w6g9-xccc-347h
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=4.3
- PyPI: `plone.app.contenttypes` — affected >=0

## Details
A privilege escalation issue in plone.app.contenttypes in Plone 4.3 through 5.2.1 allows users to PUT (overwrite) some content without needing write permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7941
- https://github.com/plone/plone.app.contenttypes
- https://github.com/plone/plone.app.contenttypes/blob/master/CHANGES.rst?plain=1#L372-L374
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2020-90.yaml
- https://plone.org/security/hotfix/20200121
- https://plone.org/security/hotfix/20200121/privilege-escalation-for-overwriting-content
- https://www.openwall.com/lists/oss-security/2020/01/22/1
- http://www.openwall.com/lists/oss-security/2020/01/24/1
