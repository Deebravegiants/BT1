# [M] Plone Sandbox Bypass

## Summary
Severity: Medium
Advisory: GHSA-9m4g-f42q-vrrh
CVE: CVE-2012-5487
CWE: CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9m4g-f42q-vrrh
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.2.3
- PyPI: `Plone` — affected >=4.3a0 <4.3b1

## Details
The sandbox whitelisting function (`allowmodule.py`) in Plone before 4.2.3 and 4.3 before beta 1 allows remote authenticated users with certain privileges to bypass the Python sandbox restriction and execute arbitrary Python code via vectors related to importing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5487
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-29.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/03
- http://www.openwall.com/lists/oss-security/2012/11/10/1
