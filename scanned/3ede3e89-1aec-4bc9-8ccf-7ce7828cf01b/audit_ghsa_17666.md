# [M] Apache Tomcat - Security constraint bypass for pre/post-resources

## Summary
Severity: Medium
Advisory: GHSA-wc4r-xq3c-5cf3
CVE: CVE-2025-49125
CWE: CWE-288
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-wc4r-xq3c-5cf3
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=11.0.0-M1 <11.0.8
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0-M1 <10.1.42
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0.M1 <9.0.106
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.8
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.42
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.106
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.0
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0

## Details
Authentication Bypass Using an Alternate Path or Channel vulnerability in Apache Tomcat.  When using PreResources or PostResources mounted other than at the root of the web application, it was possible to access those resources via an unexpected path. That path was likely not to be protected by the same security constraints as the expected path, allowing those security constraints to be bypassed.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.7, from 10.1.0-M1 through 10.1.41, from 9.0.0.M1 through 9.0.105. The following versions were EOL at the time the CVE was created but are known to be affected: 8.5.0 through 8.5.100. Other, older, EOL versions may also be affected.

Users are recommended to upgrade to version 11.0.8, 10.1.42 or 9.0.106, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49125
- https://github.com/apache/tomcat/commit/7617b9c247bc77ed0444dd69adcd8aa48777886c
- https://github.com/apache/tomcat/commit/9418e3ff9f1f4c006b4661311ae9376c52d162b9
- https://github.com/apache/tomcat/commit/d94bd36fb7eb32e790dae0339bc249069649a637
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/m66cytbfrty9k7dc4cg6tl1czhsnbywk
- https://lists.debian.org/debian-lts-announce/2025/07/msg00009.html
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-9.html
- http://www.openwall.com/lists/oss-security/2025/06/16/2
