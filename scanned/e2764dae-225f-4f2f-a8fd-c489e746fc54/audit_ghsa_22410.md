# [H] Plone Code Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-cxw7-85xm-3xrc
CVE: CVE-2012-5488
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cxw7-85xm-3xrc
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.2.3
- PyPI: `Plone` — affected >=4.3a0 <4.3b1

## Details
python_scripts.py in Plone before 4.2.3 and 4.3 before beta 1 allows remote attackers to execute Python code via a crafted URL, related to createObject.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5488
- https://github.com/plone/Products.CMFPlone/commit/a9479a5b38646fe0b0a9066ee46de9c18de32bfa
- https://github.com/plone/Products.CMFPlone/commit/c3a98f4e6cf26501485de9c8354c49afdea21df8
- https://access.redhat.com/errata/RHSA-2014:1194
- https://access.redhat.com/security/cve/CVE-2012-5488
- https://bugzilla.redhat.com/show_bug.cgi?id=878945
- https://github.com/plone/Products.CMFPlone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-30.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/04
- http://rhn.redhat.com/errata/RHSA-2014-1194.html
- http://www.openwall.com/lists/oss-security/2012/11/10/1
