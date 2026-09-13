# [C] XWiki Remote Macros vulnerable to remote code execution using the panel macro

## Summary
Severity: Critical
Advisory: CVE-2025-55728
Aliases: GHSA-48f4-h726-74p5
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-55728
Type: osv

## Details
XWiki Remote Macros provides XWiki rendering macros that are useful when migrating content from Confluence. Starting in version 1.0 and prior to version 1.26.5, missing escaping of the classes parameter in the panel macro allows remote code execution for any user who can edit any page The classes parameter is used without escaping in XWiki syntax, thus allowing XWiki syntax injection which enables remote code execution. Version 1.26.5 contains a patch for the issue.

## References
- https://github.com/xwikisas/xwiki-pro-macros/blob/93ac1a38c829e3ef787379b2b45eb043a573e5f7/xwiki-pro-macros-ui/src/main/resources/XWiki/Macros/Panel.xml#L554
- https://jira.xwiki.org/browse/XWIKI-20449
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55728.json
- https://github.com/xwikisas/xwiki-pro-macros/security/advisories/GHSA-48f4-h726-74p5
- https://nvd.nist.gov/vuln/detail/CVE-2025-55728
- https://github.com/xwikisas/xwiki-pro-macros/commit/3ca815294bf54fc024b2363efbece7aa08b8efd5
