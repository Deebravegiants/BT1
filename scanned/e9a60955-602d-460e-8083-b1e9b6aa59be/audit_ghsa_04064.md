# [M] Cross-site scripting in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-jjpq-gp5q-8q6w
CVE: CVE-2019-0221
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-05-30
Source: https://github.com/advisories/GHSA-jjpq-gp5q-8q6w
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0 <9.0.17
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <8.5.40
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=7.0.0 <7.0.94
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0 <9.0.17
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.0 <8.5.40
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=7.0.0 <7.0.94
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0 <9.0.17
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <8.5.40
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.94

## Details
The SSI printenv command in Apache Tomcat 9.0.0.M1 to 9.0.0.17, 8.5.0 to 8.5.39 and 7.0.0 to 7.0.93 echoes user provided data without escaping and is, therefore, vulnerable to XSS. SSI is disabled by default. The printenv command is intended for debugging and is unlikely to be present in a production website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0221
- https://github.com/apache/tomcat/commit/15fcd166ea2c1bb79e8541b8e1a43da9c452ceea
- https://github.com/apache/tomcat/commit/44ec74c44dcd05cd7e90967c04d40b51440ecd7e
- https://github.com/apache/tomcat/commit/4fcdf706f3ecf35912a600242f89637f5acb32da
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQTZ5BJ5F4KV6N53SGNKSW3UY5DBIQ46
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NPHQEL5AQ6LZSZD2Y6TYZ4RC3WI7NXJ3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZQTZ5BJ5F4KV6N53SGNKSW3UY5DBIQ46
- https://seclists.org/bugtraq/2019/Dec/43
- https://security.gentoo.org/glsa/202003-43
- https://security.netapp.com/advisory/ntap-20190606-0001
- https://support.f5.com/csp/article/K13184144?utm_source=f5support&amp%3Butm_medium=RSS
- https://support.f5.com/csp/article/K13184144?utm_source=f5support&amp;utm_medium=RSS
- https://tomcat.apache.org/security-7.html
- https://tomcat.apache.org/security-8.html
- https://tomcat.apache.org/security-9.html
- https://usn.ubuntu.com/4128-1
- https://usn.ubuntu.com/4128-2
- https://web.archive.org/web/20200227055048/http://www.securityfocus.com/bid/108545
- https://www.debian.org/security/2019/dsa-4596
- https://www.oracle.com/security-alerts/cpuApr2021.html
