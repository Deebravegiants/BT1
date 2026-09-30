# [C] Apache Linkis DatasourceManager module has deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-rrhf-32rq-f28h
CVE: CVE-2023-29216
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-10
Source: https://github.com/advisories/GHSA-rrhf-32rq-f28h
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis-datasource` — affected >=0 <1.3.2

## Details
In Apache Linkis <=1.3.1, because the parameters are not effectively filtered, the attacker can use the MySQL data source and malicious parameters to configure a new data source to trigger a deserialization vulnerability, eventually leading to remote code execution. Users should upgrade their version of Linkis to version 1.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29216
- https://github.com/apache/linkis
- https://linkis.apache.org/download/release-notes-1.3.2
- https://lists.apache.org/thread/18vv0m32oy51nzk8tbz13qdl5569y55l
- http://www.openwall.com/lists/oss-security/2023/04/10/5
