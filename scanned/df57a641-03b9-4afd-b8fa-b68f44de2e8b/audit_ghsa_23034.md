# [H] Plone unauthorized member addition vulnerability

## Summary
Severity: High
Advisory: GHSA-984m-rj28-8c6x
CVE: CVE-2015-7315
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-984m-rj28-8c6x
Type: github-advisory

## Affected
- PyPI: `Products.CMFPlone` — affected >=3.3.0 <4.3.7
- PyPI: `Products.CMFPlone` — affected >=5.0a1 <5.0rc2
- PyPI: `Plone` — affected >=3.3
- PyPI: `Plone` — affected >=4.0a1
- PyPI: `Plone` — affected >=4.1a1
- PyPI: `Plone` — affected >=4.2a1
- PyPI: `Plone` — affected >=4.3a1
- PyPI: `Plone` — affected 5.0rc1

## Details
Plone 3.3.0 through 3.3.6, 4.0.0 through 4.0.10, 4.1.0 through 4.1.6, 4.2.0 through 4.2.7, 4.3.0 through 4.3.6, and 5.0rc1 allows remote attackers to add a new member to a Plone site with registration enabled, without acknowledgment of site administrator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7315
- https://github.com/plone/Products.CMFPlone/commit/1845b0a92312291811b68907bf2aa0fb448c4016
- https://github.com/plone/Products.CMFPlone/commit/9f0111f85cd14f3f067044b59b93e2856c99d542
- https://github.com/zopefoundation/Products.CMFCore/commit/e1d981bfa14b664317285f0f36498f4be4a23406
- https://bugzilla.redhat.com/show_bug.cgi?id=1264791
- https://github.com/plone/Products.CMFPlone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2017-52.yaml
- https://plone.org/security/hotfix/20150910/anonymous-is-able-to-create-plone-members
- https://pypi.org/project/Products.PloneHotfix20150910
- http://www.openwall.com/lists/oss-security/2015/09/22/13
