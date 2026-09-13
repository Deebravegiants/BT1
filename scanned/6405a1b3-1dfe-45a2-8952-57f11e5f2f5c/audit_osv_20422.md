# [H] CVE-2021-33511

## Summary
Severity: High
Advisory: CVE-2021-33511
Aliases: GHSA-gc9g-67cq-p7v4, PYSEC-2021-83
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-21
Source: https://osv.dev/vulnerability/CVE-2021-33511
Type: osv

## Details
Plone though 5.2.4 allows SSRF via the lxml parser. This affects Diazo themes, Dexterity TTW schemas, and modeleditors in plone.app.theming, plone.app.dexterity, and plone.supermodel.

## References
- http://www.openwall.com/lists/oss-security/2021/05/22/1
- https://plone.org/security/hotfix/20210518/server-side-request-forgery-via-lxml-parser
