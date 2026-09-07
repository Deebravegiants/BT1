# [M] Products.CMFPlone XSS in profile home_page property

## Summary
Severity: Medium
Advisory: GHSA-859j-668v-mrr6
CVE: CVE-2017-1000482
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-859j-668v-mrr6
Type: github-advisory

## Affected
- PyPI: `Products.CMFPlone` — affected >=0 <4.3.17
- PyPI: `Products.CMFPlone` — affected >=5.0.0 <5.0.10
- PyPI: `Products.CMFPlone` — affected >=5.1a1 <5.1.0
- PyPI: `Plone` — affected >=2.5a1 <4.3.16
- PyPI: `Plone` — affected >=5.0a1 <5.1.0

## Details
A member of the Plone site could set javascript in the `home_page` property of their profile, and have this executed when a visitor clicks the home page link on the author page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000482
- https://github.com/plone/Products.CMFPlone/issues/2232
- https://github.com/plone/Products.CMFPlone/pull/2233
- https://github.com/plone/Products.CMFPlone/pull/2234
- https://github.com/plone/Products.CMFPlone/pull/2235
- https://github.com/plone/Products.CMFPlone/pull/2236
- https://github.com/plone/Products.CMFPlone/commit/05a943ecbcdda56bacc93b55c9e2e908d8a7dfab
- https://github.com/plone/Products.CMFPlone/commit/0e50e1e67ea3b6d3187f78cb1a1628081f654d3b
- https://github.com/plone/Products.CMFPlone/commit/236b62b756ff46a92783b3897e717dfb15eb07d8
- https://github.com/plone/Products.CMFPlone/commit/7db5b2c8fb684055987b8c4fdedc29289bd26373
- https://github.com/plone/Products.CMFPlone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2018-71.yaml
- https://plone.org/security/hotfix/20171128/xss-using-the-home_page-member-property
