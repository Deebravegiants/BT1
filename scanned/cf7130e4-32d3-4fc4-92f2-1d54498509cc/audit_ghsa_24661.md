# [M] Plone Filesystem path information leak

## Summary
Severity: Medium
Advisory: GHSA-rg52-j87w-pf83
CVE: CVE-2013-7060
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rg52-j87w-pf83
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=3.3 <4.3.3
- PyPI: `Products.CMFPlone` — affected >=3.3 <4.3.3

## Details
Products/CMFPlone/FactoryTool.py in Plone 3.3 through 4.3.2 allows remote attackers to obtain the installation path via vectors related to a file object for unspecified documentation which is initialized in class scope.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7060
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/b08a45bc12b1bd42411f1130a487a7a242349ea0/Products/CMFPlone/FactoryTool.py#L272-L274
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-65.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/products-cmfplone/PYSEC-2014-67.yaml
- https://plone.org/security/20131210/path-leak
- http://www.openwall.com/lists/oss-security/2013/12/10/15
- http://www.openwall.com/lists/oss-security/2013/12/12/3
