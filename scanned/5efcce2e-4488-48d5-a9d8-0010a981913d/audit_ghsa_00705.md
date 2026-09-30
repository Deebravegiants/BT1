# [H] Deserialization of untrusted data in Jackson Databind

## Summary
Severity: High
Advisory: GHSA-c265-37vj-cwcc
CVE: CVE-2020-14062
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-18
Source: https://github.com/advisories/GHSA-c265-37vj-cwcc
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.10.5

## Details
FasterXML jackson-databind 2.x before 2.9.10.5 mishandles the interaction between serialization gadgets and typing, related to com.sun.org.apache.xalan.internal.lib.sql.JNDIConnectionPool (aka xalan2).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14062
- https://github.com/FasterXML/jackson-databind/issues/2704
- https://github.com/FasterXML/jackson-databind/commit/840eae2ca81c597a0010b2126f32dce17d384b70
- https://github.com/FasterXML/jackson-databind/commit/99001cdb6807b5c7b170ec6a9092ecbb618ae79c
- https://github.com/FasterXML/jackson-databind
- https://lists.debian.org/debian-lts-announce/2020/07/msg00001.html
- https://medium.com/%40cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://medium.com/@cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://security.netapp.com/advisory/ntap-20200702-0003
- https://snyk.io/vuln/SNYK-JAVA-COMFASTERXMLJACKSONCORE-570625
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
