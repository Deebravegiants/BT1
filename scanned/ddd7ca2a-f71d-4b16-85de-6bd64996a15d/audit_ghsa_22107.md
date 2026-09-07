# [M] Exposure of Sensitive Information to an Unauthorized Actor in Oracle MySQL Connectors Java

## Summary
Severity: Medium
Advisory: GHSA-pwh7-92h3-mqr6
CVE: CVE-2017-3586
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pwh7-92h3-mqr6
Type: github-advisory

## Affected
- Maven: `mysql:mysql-connector-java` — affected >=0 <5.1.42

## Details
Vulnerability in the MySQL Connectors component of Oracle MySQL (subcomponent: Connector/J). Supported versions that are affected are 5.1.41 and earlier. Easily "exploitable" vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Connectors. While the vulnerability is in MySQL Connectors, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of MySQL Connectors accessible data as well as unauthorized read access to a subset of MySQL Connectors accessible data. CVSS 3.0 Base Score 6.4 (Confidentiality and Integrity impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3586
- http://www.debian.org/security/2017/dsa-3857
- http://www.oracle.com/technetwork/security-advisory/cpuapr2017-3236618.html
