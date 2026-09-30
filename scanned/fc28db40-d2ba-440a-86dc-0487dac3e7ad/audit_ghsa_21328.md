# [H] Apache Linkis subject to Remote Code Execution via deserialization

## Summary
Severity: High
Advisory: GHSA-3f3w-gmqf-4hj3
CVE: CVE-2022-39944
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-26
Source: https://github.com/advisories/GHSA-3f3w-gmqf-4hj3
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis` — affected >=0 <1.3.0

## Details
In Apache Linkis <=1.2.0 when used with the MySQL Connector/J, a deserialization vulnerability with possible remote code execution impact exists when an attacker has write access to a database and configures a JDBC EC with a MySQL data source and malicious parameters. Therefore, the parameters in the jdbc url should be blacklisted. This issue is patched in version 1.3.0, and users are recommended to upgrade.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-39944
- https://github.com/apache/incubator-linkis
- https://lists.apache.org/thread/rxytj48q17304snonjtyt5lnlw64gccc
