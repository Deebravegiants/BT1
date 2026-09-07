# [C] Apache Dolphinscheduler Code Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-2fm6-mv57-p2qh
CVE: CVE-2024-43202
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-20
Source: https://github.com/advisories/GHSA-2fm6-mv57-p2qh
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-task-api` — affected >=3.1.0 <3.2.2

## Details
Exposure of Remote Code Execution in Apache Dolphinscheduler.

This issue affects Apache DolphinScheduler: before 3.2.2. 

We recommend users to upgrade Apache DolphinScheduler to version 3.2.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43202
- https://github.com/apache/dolphinscheduler/pull/15758
- https://github.com/apache/dolphinscheduler/commit/c7789bf0499f5893810d93e144250544a528caa4
- https://github.com/apache/dolphinscheduler/commit/dc306bfa1d3ed72eb7b72b177e33a46042d2a9c3
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/nlmdp7q7l7o3l27778vxc5px24ncr5r5
- https://lists.apache.org/thread/qbhk9wqyxhrn4z7m4m343wqxpwg926nh
- https://www.cve.org/CVERecord?id=CVE-2023-49109
- http://www.openwall.com/lists/oss-security/2024/08/20/2
