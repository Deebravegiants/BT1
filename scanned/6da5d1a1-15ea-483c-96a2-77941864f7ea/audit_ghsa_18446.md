# [H] Apache Jackrabbit vulnerable to blind XXE attack due to insecure document build

## Summary
Severity: High
Advisory: GHSA-44c3-38h8-9fh9
CVE: CVE-2025-53689
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-14
Source: https://github.com/advisories/GHSA-44c3-38h8-9fh9
Type: github-advisory

## Affected
- Maven: `org.apache.jackrabbit:jackrabbit-spi-commons` — affected >=2.20.0 <2.20.17
- Maven: `org.apache.jackrabbit:jackrabbit-spi-commons` — affected >=2.22.0 <2.22.1
- Maven: `org.apache.jackrabbit:jackrabbit-spi-commons` — affected >=2.23.0-beta <2.23.2-beta
- Maven: `org.apache.jackrabbit:jackrabbit-core` — affected >=2.23.0-beta <2.23.2-beta
- Maven: `org.apache.jackrabbit:jackrabbit-core` — affected >=2.20.0 <2.20.17
- Maven: `org.apache.jackrabbit:jackrabbit-core` — affected >=2.22.0 <2.22.1

## Details
Blind XXE vulnerabilities in jackrabbit-spi-commons and jackrabbit-core in Apache Jackrabbit < 2.23.2 due to usage of an unsecured document build to load privileges.

Users are recommended to upgrade to versions 2.20.17 (Java 8), 2.22.1 (Java 11) or 2.23.2 (Java 11, beta versions), which fix this issue. Earlier versions (up to 2.20.16) are not supported anymore, thus users should update to the respective supported version.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53689
- https://github.com/apache/jackrabbit/pull/263/commits/02786c0a01838580252bdab79bfa54026c30294e
- https://github.com/apache/jackrabbit
- https://lists.apache.org/thread/5pf9n76ny13pzzk765og2h3gxdxw7p24
- http://www.openwall.com/lists/oss-security/2025/07/14/1
