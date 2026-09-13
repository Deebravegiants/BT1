# [H] Code Injection in jackson-databind

## Summary
Severity: High
Advisory: GHSA-h3cw-g4mq-c5x2
CVE: CVE-2020-24616
CWE: CWE-502, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-h3cw-g4mq-c5x2
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.0.0 <2.9.10.6

## Details
This project contains the general-purpose data-binding functionality and tree-model for Jackson Data Processor. FasterXML jackson-databind 2.x before 2.9.10.6 mishandles the interaction between serialization gadgets and typing, related to br.com.anteros.dbcp.AnterosDBCPDataSource (aka Anteros-DBCP).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24616
- https://github.com/FasterXML/jackson-databind/issues/2814
- https://github.com/FasterXML/jackson-databind/commit/3d97153944f7de9c19c1b3637b33d3cf1fbbe4d7
- https://github.com/FasterXML/jackson-databind
- https://lists.debian.org/debian-lts-announce/2021/04/msg00025.html
- https://medium.com/@cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://security.netapp.com/advisory/ntap-20200904-0006
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
