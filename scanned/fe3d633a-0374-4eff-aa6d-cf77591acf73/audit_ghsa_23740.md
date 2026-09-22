# [M] Plone contains Cross-site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-2q75-f7cp-w86q
CVE: CVE-2012-5500
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2q75-f7cp-w86q
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.2.3
- PyPI: `Plone` — affected >=4.3a1 <4.3b1

## Details
The batch id change script (renameObjectsByPaths.py) in Plone before 4.2.3 and 4.3 before beta 1 allows remote attackers to change the titles of content items by leveraging a valid CSRF token in a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5500
- https://access.redhat.com/errata/RHSA-2014:1194
- https://access.redhat.com/security/cve/CVE-2012-5500
- https://bugzilla.redhat.com/show_bug.cgi?id=874649
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/plone/plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-42.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/16
- http://rhn.redhat.com/errata/RHSA-2014-1194.html
- http://www.openwall.com/lists/oss-security/2012/11/10/1
