# [C] Apache OFBiz: URLs allowing remote use of Groovy expressions, leading to RCE

## Summary
Severity: Critical
Advisory: CVE-2024-47208
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2024-47208
Type: osv

## Details
Server-Side Request Forgery (SSRF), Improper Control of Generation of Code ('Code Injection') vulnerability in Apache OFBiz.

This issue affects Apache OFBiz: before 18.12.17.

Users are recommended to upgrade to version 18.12.17, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/11/16/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47208.json
- https://lists.apache.org/thread/022r19skfofhv3lzql33vowlrvqndh11
- https://nvd.nist.gov/vuln/detail/CVE-2024-47208
- https://ofbiz.apache.org/download.html
- https://issues.apache.org/jira/browse/OFBIZ-13158
- https://ofbiz.apache.org/security.html
