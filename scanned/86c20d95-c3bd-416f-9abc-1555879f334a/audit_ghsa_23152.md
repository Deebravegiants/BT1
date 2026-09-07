# [M] Plone Metadata Disclosure

## Summary
Severity: Medium
Advisory: GHSA-6w93-4c4p-xv2x
CVE: CVE-2012-5492
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6w93-4c4p-xv2x
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.2.3
- PyPI: `Plone` — affected >=4.3a0 <4.3b1

## Details
`uid_catalog.py` in Plone before 4.2.3 and 4.3 before beta 1 allows remote attackers to obtain metadata about hidden objects via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5492
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-34.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/08
- http://www.openwall.com/lists/oss-security/2012/11/10/1
