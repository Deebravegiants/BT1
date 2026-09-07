# [M] Apache Zeppelin: Arbitrary file read by adding malicious JDBC connection string

## Summary
Severity: Medium
Advisory: GHSA-jr43-q92q-5q82
CVE: CVE-2024-52279
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-08-03
Source: https://github.com/advisories/GHSA-jr43-q92q-5q82
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-jdbc` — affected >=0.11.1 <0.12.0

## Details
Improper Input Validation vulnerability in Apache Zeppelin. The fix for JDBC URL validation in CVE-2024-31864 did not account for URL encoded input.

This issue affects Apache Zeppelin: from 0.11.1 before 0.12.0.

Users are recommended to upgrade to version 0.12.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52279
- https://github.com/apache/zeppelin/pull/4838
- https://github.com/apache/zeppelin
- https://issues.apache.org/jira/browse/ZEPPELIN-6095
- https://lists.apache.org/thread/dxb98vgrb21rrl3k0fzonpk66onr6o4q
- https://www.cve.org/CVERecord?id=CVE-2024-31864
- http://www.openwall.com/lists/oss-security/2025/08/03/3
