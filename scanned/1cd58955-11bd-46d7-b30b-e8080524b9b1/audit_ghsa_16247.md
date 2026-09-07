# [M] Session Fixation Apache DolphinScheduler

## Summary
Severity: Medium
Advisory: GHSA-vjqc-g788-f378
CVE: CVE-2023-50270
CWE: CWE-613
Ecosystem: Maven
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-vjqc-g788-f378
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=1.3.8 <3.2.1

## Details
Session Fixation Apache DolphinScheduler before version 3.2.1, which session is still valid after the password change.

Users are recommended to upgrade to version 3.2.1, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50270
- https://github.com/apache/dolphinscheduler/pull/15219
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/94prw8hyk60vvw7s6cs3tr708qzqlwl6
- https://lists.apache.org/thread/lmnf21obyos920dnvbfpwq29c1sd2r9r
- https://www.openwall.com/lists/oss-security/2024/02/20/3
- http://www.openwall.com/lists/oss-security/2024/02/20/3
