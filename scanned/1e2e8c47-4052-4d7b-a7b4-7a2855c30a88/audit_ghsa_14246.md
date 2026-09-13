# [C] Apache Linkis JDBC EngineConn has deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-qm2h-m799-86rc
CVE: CVE-2023-29215
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-10
Source: https://github.com/advisories/GHSA-qm2h-m799-86rc
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis-engineconn` — affected >=0 <1.3.2

## Details
In Apache Linkis <=1.3.1, due to the lack of effective filtering of parameters, an attacker configuring malicious Mysql JDBC parameters in JDBC EngineConn Module will trigger a deserialization vulnerability and eventually lead to remote code execution. Therefore, the parameters in the Mysql JDBC URL should be blacklisted. Users should upgrade their version of Linkis to version 1.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29215
- https://github.com/apache/linkis/commit/7005c01d7f7bca78322447f4f2f32b8398645687
- https://github.com/apache/linkis
- https://linkis.apache.org/download/release-notes-1.3.2
- https://lists.apache.org/thread/o682wz1ggq491ybvjwokxvcdtnzo76ls
- http://www.openwall.com/lists/oss-security/2023/04/10/4
