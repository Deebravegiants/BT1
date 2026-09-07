# [M] Apache Ambari: Various Cross site scripting problems

## Summary
Severity: Medium
Advisory: GHSA-9q6v-rxmw-g3gh
CVE: CVE-2023-50378
CWE: CWE-20, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-01
Source: https://github.com/advisories/GHSA-9q6v-rxmw-g3gh
Type: github-advisory

## Affected
- Maven: `org.apache.ambari:ambari` — affected >=0 <2.7.8

## Details
Lack of proper input validation and constraint enforcement in Apache Ambari prior to 2.7.8  

 Impact : As it will be stored XSS, Could be exploited to perform unauthorized actions, varying from data access to session hijacking and delivering malicious payloads. 

Users are recommended to upgrade to version  2.7.8 which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50378
- https://github.com/apache/ambari
- https://lists.apache.org/thread/6hn0thq743vz9gh283s2d87wz8tqh37c
- http://www.openwall.com/lists/oss-security/2024/03/01/5
