# [M] Plone XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-38g6-x6jv-jwff
CVE: CVE-2021-29002
CWE: CWE-79
Ecosystem: PyPI
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-38g6-x6jv-jwff
Type: github-advisory

## Affected
- PyPI: `plone` — affected >=0

## Details
A stored cross-site scripting (XSS) vulnerability in Plone CMS 5.2.3 exists in site-controlpanel via the `form.widgets.site_title` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29002
- https://github.com/plone/Products.CMFPlone/issues/3255
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2021-889.yaml
- https://www.exploit-db.com/exploits/49668
