# [H] Apache DolphinScheduler: Arbitrary js execute as root for authenticated users

## Summary
Severity: High
Advisory: GHSA-v7hg-77v9-2445
CVE: CVE-2023-49299
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-30
Source: https://github.com/advisories/GHSA-v7hg-77v9-2445
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-master` — affected >=0 <3.1.9

## Details
Improper Input Validation vulnerability in Apache DolphinScheduler. An authenticated user can cause arbitrary, unsandboxed javascript to be executed on the server.This issue affects Apache DolphinScheduler: until 3.1.9.

Users are recommended to upgrade to version 3.1.9, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49299
- https://github.com/apache/dolphinscheduler/pull/15228
- https://github.com/apache/dolphinscheduler/commit/b5eddc0ce85d379080a51bf2162477f7d8c1b7d2
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/tnf99qoc6tlnwrny4t1zk6mfszgdsokm
- http://www.openwall.com/lists/oss-security/2024/02/23/3
