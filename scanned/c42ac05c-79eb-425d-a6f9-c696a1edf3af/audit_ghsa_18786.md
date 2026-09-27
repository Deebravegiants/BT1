# [H] JDBC Driver for SQL Server has improper input validation issue

## Summary
Severity: High
Advisory: GHSA-m494-w24q-6f7w
CVE: CVE-2025-59250
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-14
Source: https://github.com/advisories/GHSA-m494-w24q-6f7w
Type: github-advisory

## Affected
- Maven: `com.microsoft.sqlserver:mssql-jdbc` — affected >=8.3.0.jre11-preview <10.2.4.jre11
- Maven: `com.microsoft.sqlserver:mssql-jdbc` — affected >=11.2.0.jre11 <11.2.4.jre11
- Maven: `com.microsoft.sqlserver:mssql-jdbc` — affected >=12.2.0.jre11 <12.2.1.jre11
- Maven: `com.microsoft.sqlserver:mssql-jdbc` — affected >=12.6.0.jre11 <12.6.5.jre11
- Maven: `com.microsoft.sqlserver:mssql-jdbc` — affected >=12.8.0.jre11 <12.8.2.jre11
- Maven: `com.microsoft.sqlserver:mssql-jdbc` — affected >=12.10.0.jre11 <12.10.2.jre11
- Maven: `com.microsoft.sqlserver:mssql-jdbc` — affected >=13.2.0.jre11 <13.2.1.jre11

## Details
Improper input validation in JDBC Driver for SQL Server allows an unauthorized attacker to perform spoofing over a network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59250
- https://github.com/microsoft/mssql-jdbc/pull/2798
- https://github.com/microsoft/mssql-jdbc/pull/2800
- https://github.com/microsoft/mssql-jdbc/pull/2801
- https://github.com/microsoft/mssql-jdbc/pull/2802
- https://github.com/microsoft/mssql-jdbc/pull/2803
- https://github.com/microsoft/mssql-jdbc/pull/2807
- https://github.com/microsoft/mssql-jdbc/commit/9732e1bbc6ec44166fda2cddab31ce1c86c873dd#diff-45367b99a1951943bfecfc7765e80df687967aa56286a5b2e039f77cd9a0e118
- https://github.com/microsoft/mssql-jdbc
- https://github.com/microsoft/mssql-jdbc/blob/main/CHANGELOG.md
- https://learn.microsoft.com/en-us/sql/connect/jdbc/microsoft-jdbc-driver-for-sql-server-support-matrix
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-59250
