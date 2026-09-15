# [H] Apache DolphinScheduler: Resource File Read And Write Vulnerability

## Summary
Severity: High
Advisory: GHSA-4vv4-crw4-8pcw
CVE: CVE-2024-30188
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-4vv4-crw4-8pcw
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=3.1.0 <3.2.2

## Details
File read and write vulnerability in Apache DolphinScheduler, authenticated users can illegally access additional resource files.
This issue affects Apache DolphinScheduler: from 3.1.0 before 3.2.2.

Users are recommended to upgrade to version 3.2.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-30188
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/tbrt42mnr42bq6scxwt6bjr3s2pwyd07
