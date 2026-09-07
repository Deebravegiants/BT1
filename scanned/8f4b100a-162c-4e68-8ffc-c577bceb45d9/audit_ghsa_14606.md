# [M] Apache Tomcat vulnerable to Unprotected Transport of Credentials

## Summary
Severity: Medium
Advisory: GHSA-2c9m-w27f-53rm
CVE: CVE-2023-28708
CWE: CWE-523
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-03-22
Source: https://github.com/advisories/GHSA-2c9m-w27f-53rm
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=11.0.0-M1 <11.0.0-M3
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0-M1 <10.1.6
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0-M1 <9.0.72
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.0 <8.5.86

## Details
When using the RemoteIpFilter with requests received from a reverse proxy via HTTP that include the X-Forwarded-Proto header set to https, session cookies created by Apache Tomcat 11.0.0-M1 to 11.0.0.-M2, 10.1.0-M1 to 10.1.5, 9.0.0-M1 to 9.0.71 and 8.5.0 to 8.5.85 did not include the secure attribute. This could result in the user agent transmitting the session cookie over an insecure channel.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28708
- https://github.com/apache/tomcat/commit/3b51230764da595bb19e8d0962dd8c69ab40dfab
- https://github.com/apache/tomcat/commit/5b72c94e8b2c4ada63a1d91dc527bf4d8fd1f510
- https://github.com/apache/tomcat/commit/c64d496dda1560b5df113be55fbfaefec349b50f
- https://github.com/apache/tomcat/commit/f509bbf31fc00abe3d9f25ebfabca5e05173da5b
- https://bz.apache.org/bugzilla/show_bug.cgi?id=66471
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/hdksc59z3s7tm39x0pp33mtwdrt8qr67
- https://security.netapp.com/advisory/ntap-20230331-0012
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-8.html
- https://tomcat.apache.org/security-9.html
