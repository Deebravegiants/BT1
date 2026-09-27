# [H] Apache OFBiz: Unauthenticated endpoint could allow execution of screen rendering code

## Summary
Severity: High
Advisory: CVE-2024-38856
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-08-05
Source: https://osv.dev/vulnerability/CVE-2024-38856
Type: osv

## Details
Incorrect Authorization vulnerability in Apache OFBiz.

This issue affects Apache OFBiz: through 18.12.14.

Users are recommended to upgrade to version 18.12.15, which fixes the issue.

Unauthenticated endpoints could allow execution of screen rendering code of screens if some preconditions are met (such as when the screen definitions don't explicitly check user's permissions because they rely on the configuration of their endpoints).

## References
- http://www.openwall.com/lists/oss-security/2024/08/04/1
- https://ofbiz.apache.org/download.html
- https://ofbiz.apache.org/security.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-38856
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38856.json
- https://lists.apache.org/thread/olxxjk6b13sl3wh9cmp0k2dscvp24l7w
- https://nvd.nist.gov/vuln/detail/CVE-2024-38856
- https://issues.apache.org/jira/browse/OFBIZ-13128
