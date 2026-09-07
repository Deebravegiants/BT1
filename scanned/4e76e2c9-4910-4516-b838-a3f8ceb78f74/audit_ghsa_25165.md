# [M] Incorrect Authorization in MySQL Connector Java

## Summary
Severity: Medium
Advisory: GHSA-w6f2-8wx4-47r5
CVE: CVE-2021-2471
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w6f2-8wx4-47r5
Type: github-advisory

## Affected
- Maven: `mysql:mysql-connector-java` — affected >=8.0.0 <8.0.27

## Details
Vulnerability in the MySQL Connectors product of Oracle MySQL (component: Connector/J). Supported versions that are affected are 8.0.26 and prior. Difficult to exploit vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Connectors. Successful attacks of this vulnerability can result in unauthorized access to critical data or complete access to all MySQL Connectors accessible data and unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Connectors. CVSS 3.1 Base Score 5.9 (Confidentiality and Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:H).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-2471
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
