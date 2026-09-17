# [H] Apache Linkis DataSource's JDBC Datasource Module with DB2 has JNDI Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-7qpc-4xx9-x5qw
CVE: CVE-2023-49566
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-15
Source: https://github.com/advisories/GHSA-7qpc-4xx9-x5qw
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis-datasource` — affected >=0 <1.6.0

## Details
In Apache Linkis <=1.5.0, due to the lack of effective filteringof parameters, an attacker configuring malicious `db2` parameters in the DataSource Manager Module will result in jndi injection. Therefore, the parameters in the DB2 URL should be blacklisted. 

This attack requires the attacker to obtain an authorized account from Linkis before it can be carried out.

Versions of Apache Linkis <=1.5.0 will be affected. We recommend users upgrade the version of Linkis to version 1.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49566
- https://github.com/apache/linkis
- https://linkis.apache.org/download/release-notes-1.6.0
- https://lists.apache.org/thread/t68yy52lmv7pxgrxnq6rw7rwvk9tb1xj
- http://www.openwall.com/lists/oss-security/2024/07/13/5
