# [H] Unsafe Deserialization in jackson-databind

## Summary
Severity: High
Advisory: GHSA-vfqx-33qm-g869
CVE: CVE-2020-36189
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-vfqx-33qm-g869
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.7.0 <2.9.10.8
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=0 <2.6.7.5

## Details
FasterXML jackson-databind 2.x before 2.9.10.8 an 2.6.7.5 mishandles the interaction between serialization gadgets and typing, related to com.newrelic.agent.deps.ch.qos.logback.core.db.DriverManagerConnectionSource.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36189
- https://github.com/FasterXML/jackson-databind/issues/2996
- https://github.com/FasterXML/jackson-databind/commit/33d96c13fe18a2dad01b19ce195548c9acea9da4
- https://cowtowncoder.medium.com/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://github.com/FasterXML/jackson-databind
- https://lists.debian.org/debian-lts-announce/2021/04/msg00025.html
- https://security.netapp.com/advisory/ntap-20210205-0005
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
