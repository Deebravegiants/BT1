# [H] Plone Privilege Escallation

## Summary
Severity: High
Advisory: GHSA-cjg3-q24h-9qwf
CVE: CVE-2020-7938
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cjg3-q24h-9qwf
Type: github-advisory

## Affected
- PyPI: `plone.restapi` — affected >=0 <6.2.1
- PyPI: `Plone` — affected >=5.2.0 <5.2.2

## Details
plone.restapi in Plone 5.2.0 through 5.2.1 allows users with a certain privilege level to escalate their privileges up to the highest level.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7938
- https://github.com/plone/plone.restapi/issues/857
- https://github.com/plone/plone.restapi/pull/859
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2020-87.yaml
- https://plone.org/security/hotfix/20200121
- https://plone.org/security/hotfix/20200121/privilege-escalation-when-plone-restapi-is-installed
- https://www.openwall.com/lists/oss-security/2020/01/22/1
- http://www.openwall.com/lists/oss-security/2020/01/24/1
