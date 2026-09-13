# [M] Privilege escalation in mysql-connector-jav

## Summary
Severity: Medium
Advisory: GHSA-jcq3-cprp-m333
CVE: CVE-2019-2692
CWE: CWE-843
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-01
Source: https://github.com/advisories/GHSA-jcq3-cprp-m333
Type: github-advisory

## Affected
- Maven: `mysql:mysql-connector-java` — affected >=0 <8.0.16

## Details
Vulnerability in the MySQL Connectors component of Oracle MySQL (subcomponent: Connector/J). Supported versions that are affected are 8.0.15 and prior. Difficult to exploit vulnerability allows high privileged attacker with logon to the infrastructure where MySQL Connectors executes to compromise MySQL Connectors. Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in takeover of MySQL Connectors. CVSS 3.0 Base Score 6.3 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-2692
- https://security.netapp.com/advisory/ntap-20190423-0002
- https://snyk.io/vuln/SNYK-JAVA-MYSQL-174574
- http://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- http://www.securityfocus.com/bid/107925
