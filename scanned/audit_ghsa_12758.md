# [H] Apache Linkis contains Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-h6w8-52mq-4qxc
CVE: CVE-2022-44645
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-h6w8-52mq-4qxc
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis` — affected >=0 <1.3.1

## Details
In Apache Linkis <=1.3.0 when used with the MySQL Connector/J, a deserialization vulnerability with possible remote code execution impact exists when an attacker has write access to a database and configures new datasource with a MySQL data source and malicious parameters. Therefore, the parameters in the jdbc url should be blacklisted. Versions of Apache Linkis <= 1.3.0 will be affected. We recommend users to upgrade the version of Linkis to version 1.3.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-44645
- https://github.com/apache/linkis
- https://lists.apache.org/thread/zlcfmvt65blqc4n6fxypg6f0ns8fqfz4
