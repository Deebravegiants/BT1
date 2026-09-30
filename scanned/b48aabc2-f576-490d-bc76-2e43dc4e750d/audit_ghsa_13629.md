# [H] MySQL Connectors takeover vulnerability

## Summary
Severity: High
Advisory: GHSA-m6vm-37g8-gqvh
CVE: CVE-2023-22102
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-18
Source: https://github.com/advisories/GHSA-m6vm-37g8-gqvh
Type: github-advisory

## Affected
- Maven: `com.mysql:mysql-connector-j` — affected >=0 <8.2.0
- Maven: `mysql:mysql-connector-java` — affected >=0

## Details
Vulnerability in the MySQL Connectors product of Oracle MySQL (component: Connector/J). Supported versions that are affected are 8.1.0 and prior. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise MySQL Connectors. Successful attacks require human interaction from a person other than the attacker and while the vulnerability is in MySQL Connectors, attacks may significantly impact additional products (scope change). Successful attacks of this vulnerability can result in takeover of MySQL Connectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22102
- https://github.com/mysql/mysql-connector-j
- https://github.com/mysql/mysql-connector-j/compare/8.1.0...8.2.0
- https://security.netapp.com/advisory/ntap-20231027-0007
- https://www.oracle.com/security-alerts/cpuoct2023.html
