# [C] XWiki Platform vulnerable to privilege escalation (PR) from account through like LiveTableResults

## Summary
Severity: Critical
Advisory: CVE-2023-35152
Aliases: GHSA-rf8j-q39g-7xfm
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-06-23
Source: https://osv.dev/vulnerability/CVE-2023-35152
Type: osv

## Details
XWiki Platform is a generic wiki platform. Starting in version 12.9-rc-1 and prior to versions 14.4.8, 14.10.6, and 15.1, any logged in user can add dangerous content in their first name field and see it executed with programming rights. Leading to rights escalation. The vulnerability has been fixed on XWiki 14.4.8, 14.10.6, and 15.1. As a workaround, one may apply the patch manually.

## References
- https://jira.xwiki.org/browse/XWIKI-19900
- https://jira.xwiki.org/browse/XWIKI-20611
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35152.json
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-rf8j-q39g-7xfm
- https://nvd.nist.gov/vuln/detail/CVE-2023-35152
- https://github.com/xwiki/xwiki-platform/commit/0993a7ab3c102f9ac37ffe361a83a3dc302c0e45#diff-0b51114cb27f7a5c599cf40c59d658eae6ddc5c0836532c3b35e163f40a4854fR39
- https://github.com/xwiki/xwiki-platform/commit/6ce2d04a5779e07f6d3ed3f37d4761049b4fc3ac#diff-ef7f8b911bb8e584fda22aac5876a329add35ca0d1d32e0fdb62a439b78cfa49
