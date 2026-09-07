# [M] Cross-site scripting in Products.CMFCore, Products.PluggableAuthService, Plone

## Summary
Severity: Medium
Advisory: GHSA-35rg-466w-77h3
CVE: CVE-2021-33507
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-35rg-466w-77h3
Type: github-advisory

## Affected
- PyPI: `Products.CMFCore` — affected >=0 <2.5.1
- PyPI: `Products.PluggableAuthService` — affected >=0 <2.6.2
- PyPI: `Plone` — affected >=0

## Details
Zope Products.CMFCore before 2.5.1 and Products.PluggableAuthService before 2.6.2, as used in Plone through 5.2.4 and other products, allow Reflected XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33507
- https://github.com/advisories/GHSA-35rg-466w-77h3
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2021-79.yaml
- https://plone.org/security/hotfix/20210518/reflected-xss-in-various-spots
- http://www.openwall.com/lists/oss-security/2021/05/22/1
