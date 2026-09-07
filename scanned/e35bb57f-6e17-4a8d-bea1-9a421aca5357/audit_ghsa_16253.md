# [H] Arbitrary File Read Vulnerability in Apache Dolphinscheduler

## Summary
Severity: High
Advisory: GHSA-ff2w-wm48-jhqj
CVE: CVE-2023-51770
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-ff2w-wm48-jhqj
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=0 <3.2.1

## Details
Arbitrary File Read Vulnerability in Apache Dolphinscheduler.

This issue affects Apache DolphinScheduler: before 3.2.1. 

We recommend users to upgrade Apache DolphinScheduler to version 3.2.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51770
- https://github.com/apache/dolphinscheduler/pull/15433
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/4t8bdjqnfhldh73gy9p0whlgvnnbtn7g
- https://lists.apache.org/thread/gpks573kn00ofxn7n9gkg6o47d03p5rw
- http://www.openwall.com/lists/oss-security/2024/02/20/2
