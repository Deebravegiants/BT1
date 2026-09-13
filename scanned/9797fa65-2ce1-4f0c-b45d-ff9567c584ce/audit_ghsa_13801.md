# [M] Apache DolphinScheduler Exposure of Sensitive Information to an Unauthorized Actor vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c6cg-73p3-973h
CVE: CVE-2023-49068
CWE: CWE-200
Ecosystem: Maven
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-c6cg-73p3-973h
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-api` — affected >=0 <3.2.1

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache DolphinScheduler. This issue affects Apache DolphinScheduler: before 3.2.1.

Users are recommended to upgrade to version 3.2.1, which fixes the issue. At the time of disclosure of this advisory, this version has not yet been released. In the mean time, we recommend you make sure the logs are only available to trusted operators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49068
- https://github.com/apache/dolphinscheduler/pull/15192
- https://github.com/apache/dolphinscheduler/commit/7308888c703fbe227887d2426273100582096134
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/jn6kr6mjdgtfgpxoq9j8q4pkfsq8zmpq
