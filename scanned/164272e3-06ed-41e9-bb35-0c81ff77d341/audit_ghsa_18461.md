# [H] Apache Tomcat Catalina is vulnerable to DoS attack through bypassing of size limits

## Summary
Severity: High
Advisory: GHSA-wr62-c79q-cv37
CVE: CVE-2025-52520
CWE: CWE-190
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-wr62-c79q-cv37
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=11.0.0-M1 <11.0.9
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0-M1 <10.1.43
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0.M1 <9.0.107
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.0
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.9
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.43
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.107
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0

## Details
For some unlikely configurations of multipart upload, an Integer Overflow vulnerability in Apache Tomcat could lead to a DoS via bypassing of size limits.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.8, from 10.1.0-M1 through 10.1.42, from 9.0.0.M1 through 9.0.106. The following versions were EOL at the time the CVE was created but are known to be affected: 8.5.0 through 8.5.100. Other, older, EOL versions may also be affected.

Users are recommended to upgrade to version 11.0.9, 10.1.43 or 9.0.107, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-52520
- https://github.com/apache/tomcat/commit/927d66fbc294cb65242102b817a45fd80834e040
- https://github.com/apache/tomcat/commit/a51e4bedccfafd35b7cdd0ee3e22267dee9f90db
- https://github.com/apache/tomcat/commit/fc42bbccb9041fafd194fbfdf3eab1d44cb5c45c
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/trqq01bbxw6c92zx69kx2mw2qgmfy0o5
- https://lists.debian.org/debian-lts-announce/2025/07/msg00009.html
- http://www.openwall.com/lists/oss-security/2025/07/10/12
