# [H] Serialization gadgets exploit in jackson-databind

## Summary
Severity: High
Advisory: GHSA-r3gr-cxrf-hg25
CVE: CVE-2020-35491
CWE: CWE-502, CWE-913
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-r3gr-cxrf-hg25
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.0.0 <2.9.10.8

## Details
FasterXML jackson-databind 2.x before 2.9.10.8 mishandles the interaction between serialization gadgets and typing, related to org.apache.commons.dbcp2.datasources.SharedPoolDataSource.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35491
- https://github.com/FasterXML/jackson-databind/issues/2986
- https://github.com/FasterXML/jackson-databind/commit/41b8bdb5ccc1d8edb71acf1c8234da235a24249d
- https://cowtowncoder.medium.com/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://github.com/FasterXML/jackson-databind
- https://lists.debian.org/debian-lts-announce/2021/04/msg00025.html
- https://security.netapp.com/advisory/ntap-20210122-0005
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
