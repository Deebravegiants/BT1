# [M] Apache Hive Incorrectly Assigns Permissions for a Critical Resource

## Summary
Severity: Medium
Advisory: GHSA-c476-j253-5rgq
CVE: CVE-2024-29869
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-c476-j253-5rgq
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive-exec` — affected >=0 <4.0.1

## Details
Hive creates a credentials file to a temporary directory in the file system with permissions 644 by default when the file permissions are not set explicitly. Any unauthorized user having access to the directory can read the sensitive information written into this file. Users are recommended to upgrade to version 4.0.1, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29869
- https://github.com/apache/hive/commit/20106e254527f7d71b2e34455c4322e14950c620
- https://github.com/apache/hive
- https://issues.apache.org/jira/browse/HIVE-28134
- https://lists.apache.org/thread/h27ohpyrqf9w1m3c0tqr7x8jg59rcrv6
- http://www.openwall.com/lists/oss-security/2025/01/28/4
