# [H] Plone Unrestricted Filed Manipulation vulnerability via content edit forms

## Summary
Severity: High
Advisory: GHSA-6fgf-x7wg-hp8r
CVE: CVE-2013-4193
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6fgf-x7wg-hp8r
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=2.1 <4.1.1
- PyPI: `Plone` — affected >=4.2 <4.2.6
- PyPI: `Plone` — affected >=4.3 <4.3.2

## Details
typeswidget.py in Plone 2.1 through 4.1, 4.2.x through 4.2.5, and 4.3.x through 4.3.1 does not properly enforce the immutable setting on unspecified content edit forms, which allows remote attackers to hide fields on the forms via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4193
- https://bugzilla.redhat.com/show_bug.cgi?id=978469
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-57.yaml
- http://plone.org/products/plone-hotfix/releases/20130618
- http://plone.org/products/plone/security/advisories/20130618-announcement
- http://seclists.org/oss-sec/2013/q3/261
