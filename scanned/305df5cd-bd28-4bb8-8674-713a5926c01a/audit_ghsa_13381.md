# [M] Apache InLong SQL Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cqr6-3x3f-9wr3
CVE: CVE-2023-30465
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-cqr6-3x3f-9wr3
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.4.0 <1.6.0
- Maven: `org.apache.inlong:manager-service` — affected >=1.4.0 <1.6.0

## Details
Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.4.0 through 1.5.0. By manipulating the "orderType" parameter and the ordering of the returned content using an SQL injection attack, an attacker can extract the username of the   user with ID 1 from the "user" table, one character at a time.  Users are advised to upgrade to Apache InLong's 1.6.0 or cherry-pick PR #7530 to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30465
- https://github.com/apache/inlong/issues/7529
- https://github.com/apache/inlong/pull/7530
- https://github.com/apache/inlong
- https://inlong.apache.org/zh-CN/download/release-1.6.0
- https://lists.apache.org/thread/mrh4nr3jrlbj6nxkn4q8hddbfh1pnok0
- http://www.openwall.com/lists/oss-security/2023/04/11/2
