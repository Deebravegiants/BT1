# [M] Apache DolphinScheduler: An incorrect authorization vulnerability allows authenticated users to access alert instances associated with alert groups they do not have permission to access.

## Summary
Severity: Medium
Advisory: GHSA-694g-j8pj-cjj5
CVE: CVE-2026-47340
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-694g-j8pj-cjj5
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-api` — affected >=0 <3.4.2

## Details
Allow authenticated users to access alert instances associated with alert groups they do not have permission to access. in Apache DolphinScheduler.

This issue affects Apache DolphinScheduler: before 3.4.2.

Users are recommended to upgrade to version 3.4.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-47340
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/gx6v1wjb6qg3fzksxomysspy2gw54ooc
- http://www.openwall.com/lists/oss-security/2026/06/17/5
