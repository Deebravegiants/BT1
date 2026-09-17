# [H] Plone and Zope2 affected by Race Condition

## Summary
Severity: High
Advisory: GHSA-3qpr-7rmg-73v8
CVE: CVE-2012-5507
CWE: CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-3qpr-7rmg-73v8
Type: github-advisory

## Affected
- PyPI: `Zope2` — affected >=0 <2.13.19
- PyPI: `Plone` — affected >=3.2.2 <4.2.3
- PyPI: `Plone` — affected >=4.3a1 <4.3b1

## Details
AccessControl/AuthEncoding.py in Zope before 2.13.19, as used in Plone before 4.2.3 and 4.3 before beta 1, allows remote attackers to obtain passwords via vectors involving timing discrepancies in password validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5507
- https://bugs.launchpad.net/zope2/+bug/1071067
- https://github.com/advisories/GHSA-3qpr-7rmg-73v8
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-49.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/zope2/PYSEC-2014-75.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/23
- http://www.openwall.com/lists/oss-security/2012/11/10/1
