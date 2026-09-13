# [H] Apache OFBiz: DataResource Low-Privileged Authenticated FreeMarker Template Injection Leads to Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2026-50223
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-50223
Type: osv

## Details
Improper Control of Generation of Code ('Code Injection') vulnerability in Apache OFBiz allows a low-privileged authenticated user with Content/DataResource editing privileges to perform template injection attacks that could lead to Remote Code Execution.

This issue affects Apache OFBiz: before 24.09.07.

Users are recommended to upgrade to version 24.09.07, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/10/13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50223.json
- https://lists.apache.org/thread/trr2p4zokg54glqlhjnglt4yr7n8t5xd
- https://nvd.nist.gov/vuln/detail/CVE-2026-50223
