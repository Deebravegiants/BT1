# [M] Plone XSS in Zope ZMI

## Summary
Severity: Medium
Advisory: GHSA-84jm-cpc5-c7g7
CVE: CVE-2016-7147
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-84jm-cpc5-c7g7
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=4.0 <4.3.12
- PyPI: `Plone` — affected >=5.0 <5.0.7

## Details
Cross-site scripting (XSS) vulnerability in the manage_findResult component in the search feature in Zope ZMI in Plone before 4.3.12 and 5.x before 5.0.7 allows remote attackers to inject arbitrary web script or HTML via vectors involving double quotes, as demonstrated by the `obj_ids:tokens` parameter. NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-7140.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7147
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2017-64.yaml
- https://plone.org/security/hotfix/20170117
- https://plone.org/security/hotfix/20170117/non-persistent-xss-in-zope2
- https://web.archive.org/web/20170214002551/http://www.securityfocus.com/bid/96117
- http://www.curesec.com/blog/article/blog/Plone-XSS-186.html
