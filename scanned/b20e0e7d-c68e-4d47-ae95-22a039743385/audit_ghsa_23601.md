# [H] Apache Tomcat EncryptInterceptor error leads to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-r84p-88g2-2vx2
CVE: CVE-2022-29885
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r84p-88g2-2vx2
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0-M1 <10.1.0-M15
- Maven: `org.apache.tomcat:tomcat` — affected >=10.0.0-M1 <10.0.21
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.13 <9.0.63
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.38 <8.5.79

## Details
The documentation of Apache Tomcat 10.1.0-M1 to 10.1.0-M14, 10.0.0-M1 to 10.0.20, 9.0.13 to 9.0.62 and 8.5.38 to 8.5.78 for the EncryptInterceptor incorrectly stated it enabled Tomcat clustering to run over an untrusted network. This was not correct. While the EncryptInterceptor does provide confidentiality and integrity protection, it does not protect against all risks associated with running over any untrusted network, particularly DoS risks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29885
- https://github.com/apache/tomcat/commit/0fa7721f11d565a2cd2e44366c388ad6a3e6357d
- https://github.com/apache/tomcat/commit/36826ea638457d7e17876a70f89cb435b6db0d91
- https://github.com/apache/tomcat/commit/b679bc627f5a4ea6510af95adfb7476b07eba890
- https://github.com/apache/tomcat/commit/eaafd28296c54d983e28a47953c1f5cb2c334f48
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/2b4qmhbcyqvc7dyfpjyx54c03x65vhcv
- https://lists.debian.org/debian-lts-announce/2022/10/msg00029.html
- https://security.netapp.com/advisory/ntap-20220629-0002
- https://www.debian.org/security/2022/dsa-5265
- https://www.oracle.com/security-alerts/cpujul2022.html
