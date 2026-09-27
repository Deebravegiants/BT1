# [M] Apache OFBiz: RCE Vulnerability in scrum plugin

## Summary
Severity: Medium
Advisory: CVE-2025-54466
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-08-15
Source: https://osv.dev/vulnerability/CVE-2025-54466
Type: osv

## Details
Improper Control of Generation of Code ('Code Injection') vulnerability leading to a possible RCE in Apache OFBiz scrum plugin.

This issue affects Apache OFBiz: before 24.09.02 only when the scrum plugin is used.

Even unauthenticated attackers can exploit this vulnerability.


Users are recommended to upgrade to version 24.09.02, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/08/05/1
- https://ofbiz.apache.org/download.html
- https://ofbiz.apache.org/security.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54466.json
- https://lists.apache.org/thread/14d0yd9co9gx2mctd3vyz1cc8d39n915
- https://nvd.nist.gov/vuln/detail/CVE-2025-54466
- https://ofbiz.apache.org/release-notes-24.09.02.html
- https://issues.apache.org/jira/browse/OFBIZ-13276
