# [M] Products.CMFPlone Open Redirect Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8g72-gq68-6gqh
CVE: CVE-2017-1000481
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8g72-gq68-6gqh
Type: github-advisory

## Affected
- PyPI: `Products.CMFPlone` — affected >=0 <4.3.17
- PyPI: `Products.CMFPlone` — affected >=5.0.0 <5.0.10
- PyPI: `Products.CMFPlone` — affected >=5.1a1 <5.1.0
- PyPI: `Plone` — affected >=2.5 <4.3.16
- PyPI: `Plone` — affected >=5 <5.1.0

## Details
When you visit a page where you need to login, Plone 2.5-5.1rc1 sends you to the login form with a 'came_from' parameter set to the previous url. After you login, you get redirected to the page you tried to view before. An attacker might try to abuse this by letting you click on a specially crafted link. You would login, and get redirected to the site of the attacker, letting you think that you are still on the original Plone site. Or some javascript of the attacker could be executed. Most of these types of attacks are already blocked by Plone, using the `isURLInPortal` check to make sure we only redirect to a page on the same Plone site. But a few more ways of tricking Plone into accepting a malicious link were discovered, and fixed with this hotfix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000481
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
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2018-70.yaml
- https://plone.org/security/hotfix/20171128/open-redirection-on-login-form
