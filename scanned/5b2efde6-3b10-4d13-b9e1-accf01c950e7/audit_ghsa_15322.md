# [H] Apache Inlong Code Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-qff2-8qw7-hcvw
CVE: CVE-2024-36268
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2024-08-02
Source: https://github.com/advisories/GHSA-qff2-8qw7-hcvw
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:tubemq-core` — affected >=1.10.0 <1.13.0

## Details
Improper Control of Generation of Code ('Code Injection') vulnerability in Apache InLong.

This issue affects Apache InLong: from 1.10.0 through 1.12.0, which could lead to Remote Code Execution. Users are advised to upgrade to Apache InLong's 1.13.0 or cherry-pick [1] to solve it.

[1]  https://github.com/apache/inlong/pull/10251

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36268
- https://github.com/apache/inlong/pull/10251
- https://github.com/apache/inlong/commit/85fc8b02e69badc5103fadb77559a921c788537a
- https://lists.apache.org/thread/1w1yp1bg5sjvn46dszkf00tz1vfs0frc
