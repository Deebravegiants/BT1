# [M] Plone Privilege escalation through exposed underlying API

## Summary
Severity: Medium
Advisory: GHSA-4vr8-r7qr-fpvq
CVE: CVE-2013-7061
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4vr8-r7qr-fpvq
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=3.3b1 <4.3.3
- PyPI: `Products.CMFPlone` — affected >=3.3 <4.3.3

## Details
`Products/CMFPlone/CatalogTool.py` in Plone 3.3 through 4.3.2 allows remote administrators to bypass restrictions and obtain sensitive information via an unspecified search API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7061
- https://github.com/plone/Products.CMFPlone/commit/a6a3e50f759da7e7ca46e50777a35e51f4d8ed48
- https://github.com/plone/Products.CMFPlone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-66.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/products-cmfplone/PYSEC-2014-68.yaml
- https://plone.org/security/20131210/catalogue-exposure
- https://pypi.org/project/Products.PloneHotfix20131210
- http://www.openwall.com/lists/oss-security/2013/12/10/15
- http://www.openwall.com/lists/oss-security/2013/12/12/3
