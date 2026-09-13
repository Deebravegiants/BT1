# [M] Apache InLong: General user can delete and update process

## Summary
Severity: Medium
Advisory: GHSA-86pw-4rqp-6x7v
CVE: CVE-2023-34189
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-86pw-4rqp-6x7v
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:inlong-manager` — affected >=1.4.0 <1.8.0

## Details
Exposure of Resource to Wrong Sphere Vulnerability in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.4.0 through 1.7.0. The attacker could use general users to delete and update the process, which only the admin can operate occurrences. 

Users are advised to upgrade to Apache InLong's 1.8.0 or cherry-pick  https://github.com/apache/inlong/pull/8109  to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34189
- https://github.com/apache/inlong/issues/8108
- https://github.com/apache/inlong/pull/8109
- https://github.com/apache/inlong
- https://lists.apache.org/thread/smxqyx43hxjvzv4w71n2n3rfho9p378s
- http://www.openwall.com/lists/oss-security/2023/07/25/2
