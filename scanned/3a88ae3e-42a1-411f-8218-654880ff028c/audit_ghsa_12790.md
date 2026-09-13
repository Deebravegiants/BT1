# [M] Apache Linkis vulnerable to Exposure of Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-rx76-xw35-6rh8
CVE: CVE-2022-44644
CWE: CWE-20, CWE-200, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-rx76-xw35-6rh8
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis` — affected >=0 <1.3.1

## Details
In Apache Linkis <=1.3.0 when used with the MySQL Connector/J, an authenticated attacker could read arbitrary local file by connecting a rogue mysql server, By adding allowLoadLocalInfile to true in the jdbc parameter. Therefore, the parameters in the jdbc url should be blacklisted. Versions of Apache Linkis <= 1.3.0 will be affected. We recommend users upgrade the version of Linkis to version 1.3.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-44644
- https://github.com/apache/linkis
- https://lists.apache.org/thread/hwq9ytq6y1kdh9lz5znptkcrdll9x85h
