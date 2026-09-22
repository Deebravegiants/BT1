# [M] Apache Flink CDC is vulnerable to SQL Injection through maliciously crafted identifiers

## Summary
Severity: Medium
Advisory: GHSA-wqm3-w3p6-xjgm
CVE: CVE-2025-62228
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:L/VA:L/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-wqm3-w3p6-xjgm
Type: github-advisory

## Affected
- Maven: `org.apache.flink:flink-cdc-pipeline-connectors` — affected >=3.0.0 <3.5.0
- Maven: `org.apache.flink:flink-connector-oracle-cdc` — affected >=3.0.0 <3.5.0
- Maven: `org.apache.flink:flink-connector-db2-cdc` — affected >=3.0.0 <3.5.0
- Maven: `org.apache.flink:flink-connector-sqlserver-cdc` — affected >=3.0.0 <3.5.0
- Maven: `org.apache.flink:flink-connector-mysql-cdc` — affected >=3.0.0 <3.5.0

## Details
Apache Flink CDC version 3.0.0 to before 3.5.0 are vulnerable to a SQL injection via maliciously crafted identifiers eg. crafted database name or crafted table name. Even through only the logged-in database user can trigger the attack, users are recommended to update Flink CDC version to 3.5.0 which address this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62228
- https://github.com/apache/flink-cdc/pull/4123
- https://github.com/apache/flink-cdc/commit/d5766187a9a4b191820e10238d4594ae665cdb89
- https://github.com/apache/flink-cdc
- https://lists.apache.org/thread/3dn0hc1wbc5sj0jbgdg33gtnwlw7qrl3
- http://www.openwall.com/lists/oss-security/2025/10/09/2
