# [H] Improper socket reuse in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-h3ch-5pp2-vh6w
CVE: CVE-2022-25762
CWE: CWE-404
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h3ch-5pp2-vh6w
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <8.5.75
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0M1 <9.0.20

## Details
If a web application sends a WebSocket message concurrently with the WebSocket connection closing when running on Apache Tomcat 8.5.0 to 8.5.75 or Apache Tomcat 9.0.0.M1 to 9.0.20, it is possible that the application will continue to use the socket after it has been closed. The error handling triggered in this case could cause the a pooled object to be placed in the pool twice. This could result in subsequent connections using the same object concurrently which could result in data being returned to the wrong use and/or other errors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25762
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/6ckmjfb1k61dyzkto9vm2k5jvt4o7w7c
- https://security.netapp.com/advisory/ntap-20220629-0003
- https://www.oracle.com/security-alerts/cpujul2022.html
