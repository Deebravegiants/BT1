# [M] Apache Linkis Metadata Query Service JDBC: JDBC Datasource Module with Mysql has file read vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8cvq-3jjp-ph9p
CVE: CVE-2024-45627
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-8cvq-3jjp-ph9p
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis-metadata-query-service-jdbc` — affected >=1.5.0 <1.7.0

## Details
# Affected versions:

- Apache Linkis Metadata Query Service JDBC 1.5.0 before 1.7.0

# Description:

In Apache Linkis <1.7.0, due to the lack of effective filtering of parameters, an attacker configuring malicious Mysql JDBC parameters in the DataSource Manager Module will allow the attacker to read arbitrary files from the Linkis server. Therefore, the parameters in the Mysql JDBC URL should be blacklisted. This attack requires the attacker to obtain an authorized account from Linkis before it can be carried out. Versions of Apache Linkis < 1.6.0 will be affected.

We recommend users upgrade the version of Linkis to version 1.7.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45627
- https://github.com/apache/linkis
- https://lists.apache.org/thread/0zzx8lldwoqgzq98mg61hojgpvn76xsh
- http://www.openwall.com/lists/oss-security/2025/01/14/1
