# [M] Plone Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-f8pg-wp5j-rjxx
CVE: CVE-2012-5491
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f8pg-wp5j-rjxx
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.2.3
- PyPI: `Plone` — affected >=4.3a0 <4.3b1

## Details
`z3c.form`, as used in Plone before 4.2.3 and 4.3 before beta 1, allows remote attackers to obtain the default form field values by leveraging knowledge of the form location and the element id.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5491
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-33.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/07
- http://www.openwall.com/lists/oss-security/2012/11/10/1
