# [C] Apache DolphinScheduler: The `/v2` experimental interface lacks permission checks

## Summary
Severity: Critical
Advisory: GHSA-85g9-8j9g-p486
CVE: CVE-2026-32967
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-85g9-8j9g-p486
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-api` — affected >=0 <3.4.2

## Details
Incorrect Authorization vulnerability of `/v2` experimental interface in Apache DolphinScheduler.

This issue affects Apache DolphinScheduler: before 3.4.2.

Users are recommended to upgrade to version 3.4.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-32967
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/5o5jrg1snkmrto96wg015wgbh7hyckzc
- http://www.openwall.com/lists/oss-security/2026/06/17/3
