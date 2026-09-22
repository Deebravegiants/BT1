# [M] Plone User account enumeration via crafted URL

## Summary
Severity: Medium
Advisory: GHSA-683w-84m7-p8pw
CVE: CVE-2012-5497
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-683w-84m7-p8pw
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.2.3
- PyPI: `Plone` — affected >=4.3a1 <4.3b1

## Details
membership_tool.py in Plone before 4.2.3 and 4.3 before beta 1 allows remote attackers to enumerate user account names via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5497
- https://github.com/plone/Products.CMFPlone/commit/a9479a5b38646fe0b0a9066ee46de9c18de32bfa
- https://github.com/plone/Products.CMFPlone/commit/c3a98f4e6cf26501485de9c8354c49afdea21df8
- https://access.redhat.com/errata/RHSA-2014:1194
- https://access.redhat.com/security/cve/CVE-2012-5497
- https://bugzilla.redhat.com/show_bug.cgi?id=874681
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-39.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/13
- https://web.archive.org/web/20131103175056/https://plone.org/products/plone/security/advisories/20121106/13
- https://web.archive.org/web/20131114082527/https://plone.org/products/plone-hotfix/releases/20121106
- http://rhn.redhat.com/errata/RHSA-2014-1194.html
- http://www.openwall.com/lists/oss-security/2012/11/10/1
