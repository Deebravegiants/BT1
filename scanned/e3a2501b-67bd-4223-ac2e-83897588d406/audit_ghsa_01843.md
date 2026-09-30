# [H] Serialization gadget exploit in jackson-databind

## Summary
Severity: High
Advisory: GHSA-5r5r-6hpj-8gg9
CVE: CVE-2020-35728
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-5r5r-6hpj-8gg9
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.0.0 <2.9.10.8

## Details
FasterXML jackson-databind 2.x before 2.9.10.8 mishandles the interaction between serialization gadgets and typing, related to com.oracle.wls.shaded.org.apache.xalan.lib.sql.JNDIConnectionPool (aka embedded Xalan in org.glassfish.web/javax.servlet.jsp.jstl).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35728
- https://github.com/FasterXML/jackson-databind/issues/2999
- https://github.com/FasterXML/jackson-databind/commit/1ca0388c2fb37ac6a06f1c188ae89c41e3e15e84
- https://github.com/FasterXML/jackson-databind
- https://lists.debian.org/debian-lts-announce/2021/04/msg00025.html
- https://medium.com/@cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://security.netapp.com/advisory/ntap-20210129-0007
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
