# [M] ClickHouse vulnerable to client certificate password exposure in client exception

## Summary
Severity: Medium
Advisory: GHSA-g8ph-74m6-8m7r
CVE: CVE-2024-23689
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-05-12
Source: https://github.com/advisories/GHSA-g8ph-74m6-8m7r
Type: github-advisory

## Affected
- Maven: `com.clickhouse:clickhouse-client` — affected >=0 <0.4.6
- Maven: `com.clickhouse:clickhouse-jdbc` — affected >=0 <0.4.6
- Maven: `com.clickhouse:clickhouse-r2dbc` — affected >=0 <0.4.6

## Details
### Summary
As initially reported in issue #1331, when client certificate authentication is enabled with password protection, the password (referred to as the client option `sslkey`) may be exposed in client exceptions (e.g., ClickHouseException or SQLException). This vulnerability can potentially lead to unauthorized access, data breaches, and violations of user privacy.

### Details
During the handling of ClickHouseException, the client certificate password may be inadvertently exposed when sslkey is specified. This issue can arise when an exception is thrown during the execution of a query or a database operation. The client certificate password is then included in the exception message, which could be logged or exposed to unauthorized parties.

### Impact
This vulnerability enables an attacker with access to client exception error messages or logs to obtain client certificate passwords, potentially allowing unauthorized access to sensitive information, data manipulation, and denial of service attacks. The extent of the risk depends on the specific implementation and usage of the affected systems. However, any exposure of client certificate passwords should be treated as a high-priority security concern.

## References
- https://github.com/ClickHouse/clickhouse-java/security/advisories/GHSA-g8ph-74m6-8m7r
- https://nvd.nist.gov/vuln/detail/CVE-2024-23689
- https://github.com/ClickHouse/clickhouse-java/issues/1331
- https://github.com/ClickHouse/clickhouse-java/pull/1334
- https://github.com/ClickHouse/clickhouse-java
- https://github.com/ClickHouse/clickhouse-java/releases/tag/v0.4.6
- https://vulncheck.com/advisories/vc-advisory-GHSA-g8ph-74m6-8m7r
