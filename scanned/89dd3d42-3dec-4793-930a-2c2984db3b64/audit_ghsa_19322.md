# [M] Apache InLong: JDBC Vulnerability For URLEncode and backspace bypass

## Summary
Severity: Medium
Advisory: GHSA-532x-j9r7-8f73
CVE: CVE-2025-27526
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-532x-j9r7-8f73
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.13.0 <2.2.0

## Details
Deserialization of Untrusted Data vulnerability in Apache InLong.

This issue affects Apache InLong: from 1.13.0 through 2.1.0. This vulnerability which can lead to JDBC Vulnerability URLEncode and backspace bypass. Users are advised to upgrade to Apache InLong's 2.2.0 or cherry-pick [1] to solve it.

[1]  https://github.com/apache/inlong/pull/11747

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27526
- https://github.com/apache/inlong/pull/11747
- https://github.com/apache/inlong/commit/48c2f5cad4a92be2c3561174d70cdbc91a2d2626
- https://github.com/apache/inlong
- https://lists.apache.org/thread/4t4sqscm7xdqn883dyjy40qk6ncf26xf
- http://www.openwall.com/lists/oss-security/2025/05/28/1
