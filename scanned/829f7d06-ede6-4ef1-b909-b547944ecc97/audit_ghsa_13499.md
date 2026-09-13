# [M] Apache Tomcat Incomplete Cleanup vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g8pj-r55q-5c2v
CVE: CVE-2023-42795
CWE: CWE-459
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-g8pj-r55q-5c2v
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0-M1 <11.0.0-M12
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0-M1 <10.1.14
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0-M1 <9.0.81
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <8.5.94
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.14
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0-M1 <9.0.81
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <8.5.94
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.0-M12
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=11.0.0-M1 <11.0.0-M12
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0-M1 <10.1.14
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0-M1 <9.0.81
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.0 <8.5.94
- Maven: `org.apache.tomcat:tomcat-util` — affected >=11.0.0-M1 <11.0.0-M12
- Maven: `org.apache.tomcat:tomcat-util` — affected >=10.1.0-M1 <10.1.14
- Maven: `org.apache.tomcat:tomcat-util` — affected >=9.0.0-M1 <9.0.81
- Maven: `org.apache.tomcat:tomcat-util` — affected >=8.5.0 <8.5.94

## Details
Incomplete Cleanup vulnerability in Apache Tomcat.

When recycling various internal objects in Apache Tomcat from 11.0.0-M1 through 11.0.0-M11, from 10.1.0-M1 through 10.1.13, from 9.0.0-M1 through 9.0.80 and from 8.5.0 through 8.5.93, an error could cause Tomcat to skip some parts of the recycling process leading to information leaking from the current request/response to the next.  Older, EOL versions may also be affected.

Users are recommended to upgrade to version 11.0.0-M12 onwards, 10.1.14 onwards, 9.0.81 onwards or 8.5.94 onwards, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42795
- https://github.com/apache/tomcat/commit/30f8063d7a9b4c43ae4722f5e382a76af1d7a6bf
- https://github.com/apache/tomcat/commit/44d05d75d696ca10ce251e4e370511e38f20ae75
- https://github.com/apache/tomcat/commit/9375d67106f8df9eb9d7b360b2bef052fe67d3d4
- https://github.com/apache/tomcat/commit/d6db22e411307c97ddf78315c15d5889356eca38
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/065jfyo583490r9j2v73nhpyxdob56lw
- https://lists.debian.org/debian-lts-announce/2023/10/msg00020.html
- https://security.netapp.com/advisory/ntap-20231103-0007
- https://www.debian.org/security/2023/dsa-5521
- https://www.debian.org/security/2023/dsa-5522
- http://www.openwall.com/lists/oss-security/2023/10/10/9
