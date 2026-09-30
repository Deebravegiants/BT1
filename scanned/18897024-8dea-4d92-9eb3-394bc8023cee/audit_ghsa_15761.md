# [H] Apache Linkis DataSource allows arbitrary file reading

## Summary
Severity: High
Advisory: GHSA-f22j-9j59-33j4
CVE: CVE-2023-41916
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-15
Source: https://github.com/advisories/GHSA-f22j-9j59-33j4
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis-datasource` — affected >=1.4.0 <1.6.0

## Details
In Apache Linkis = 1.4.0, due to the lack of effective filtering of parameters, an attacker configuring malicious Mysql JDBC parameters in the DataSource Manager Module will trigger arbitrary file reading. Therefore, the parameters in the Mysql JDBC URL should be blacklisted. This attack requires the attacker to obtain an authorized account from Linkis before it can be carried out. 

Versions of Apache Linkis = 1.4.0 will be affected. 

We recommend users upgrade the version of Linkis to version 1.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41916
- https://github.com/apache/linkis
- https://linkis.apache.org/download/release-notes-1.6.0
- https://lists.apache.org/thread/dxkpwyoxy1jpdwlpqp15zvo0jxn4v729
- http://www.openwall.com/lists/oss-security/2024/07/13/4
