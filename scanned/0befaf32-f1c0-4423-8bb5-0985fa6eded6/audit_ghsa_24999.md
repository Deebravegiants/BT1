# [M] Plone's authenticated users able to alter their password despite of policy definition

## Summary
Severity: Medium
Advisory: GHSA-qjxf-6pr8-j87v
CVE: CVE-2013-4198
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qjxf-6pr8-j87v
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=2.1
- PyPI: `Plone` — affected >=4.2 <4.2.6
- PyPI: `Plone` — affected >=4.3 <4.3.2

## Details
`mail_password.py` in Plone 2.1 through 4.1, 4.2.x through 4.2.5, and 4.3.x through 4.3.1 allows remote authenticated users to bypass the prohibition on password changes via the forgotten password email functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4198
- https://bugzilla.redhat.com/show_bug.cgi?id=978480
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-62.yaml
- https://pypi.org/project/Products.PloneHotfix20130618
- http://plone.org/products/plone-hotfix/releases/20130618
- http://plone.org/products/plone/security/advisories/20130618-announcement
- http://seclists.org/oss-sec/2013/q3/261
