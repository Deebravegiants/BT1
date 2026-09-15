# [H] jackson-databind mishandles the interaction between serialization gadgets and typing

## Summary
Severity: High
Advisory: GHSA-58pp-9c76-5625
CVE: CVE-2020-11112
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-58pp-9c76-5625
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.10.4

## Details
FasterXML jackson-databind 2.x before 2.9.10.4 mishandles the interaction between serialization gadgets and typing, related to org.apache.commons.proxy.provider.remoting.RmiProvider (aka apache/commons-proxy).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11112
- https://github.com/FasterXML/jackson-databind/issues/2666
- https://github.com/FasterXML/jackson-databind
- https://lists.debian.org/debian-lts-announce/2020/04/msg00012.html
- https://medium.com/@cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://security.netapp.com/advisory/ntap-20200403-0002
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
