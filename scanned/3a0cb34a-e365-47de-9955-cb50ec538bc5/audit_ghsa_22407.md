# [H] Plone Information Disclosure

## Summary
Severity: High
Advisory: GHSA-cq5g-924m-7fxh
CVE: CVE-2012-5505
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cq5g-924m-7fxh
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.2.3
- PyPI: `Plone` — affected >=4.3a0 <4.3b1

## Details
`atat.py` in Plone before 4.2.3 and 4.3 before beta 1 allows remote attackers to read private data structures via a request for a view without a name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5505
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-47.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/21
- http://www.openwall.com/lists/oss-security/2012/11/10/1
