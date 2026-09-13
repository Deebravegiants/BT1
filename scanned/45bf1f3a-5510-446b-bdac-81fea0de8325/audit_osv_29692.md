# [H] Apache OFBiz: Prevent use of URLs in files when loading them from Java or Groovy, leading to a RCE

## Summary
Severity: High
Advisory: CVE-2024-45507
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-45507
Type: osv

## Details
Server-Side Request Forgery (SSRF), Improper Control of Generation of Code ('Code Injection') vulnerability in Apache OFBiz.

This issue affects Apache OFBiz: before 18.12.16.

Users are recommended to upgrade to version 18.12.16, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/09/03/7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45507.json
- https://lists.apache.org/thread/o90dd9lbk1hh3t2557t2y2qvrh92p7wy
- https://nvd.nist.gov/vuln/detail/CVE-2024-45507
- https://ofbiz.apache.org/download.html
- https://issues.apache.org/jira/browse/OFBIZ-13132
- https://ofbiz.apache.org/security.html
