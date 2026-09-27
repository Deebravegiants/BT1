# [H] Apache Tomcat: Padding Oracle vulnerability in EncryptInterceptor

## Summary
Severity: High
Advisory: GHSA-h468-7pvh-8vr8
CVE: CVE-2026-29146
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-h468-7pvh-8vr8
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=9.0.13 <9.0.116
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=10.1.50 <10.1.53
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=11.0.0-M1 <11.0.20
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.13 <9.0.116
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.50 <10.1.53
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0-M1 <11.0.20
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=8.5.38
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.38
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=7.0.100
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.100

## Details
Padding Oracle vulnerability in Apache Tomcat's EncryptInterceptor with default configuration.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.18, from 10.0.0-M1 through 10.1.52, from 9.0.13 through 9..115, from 8.5.38 through 8.5.100, from 7.0.100 through 7.0.109.

Users are recommended to upgrade to version 11.0.19, 10.1.53 and 9.0.116, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-29146
- https://github.com/apache/tomcat/commit/0112ed22abfccc3d54e44d91eb08804d0886acd1
- https://github.com/apache/tomcat/commit/607ebc0fa522bd9e8c05517baa2d179bbd1e659c
- https://github.com/apache/tomcat/commit/6d955cceca841f2eabf2d6c46b59a8c7e1cd6eaa
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/lzt04z2pb3dc5tk85obn80xygw3z1p0w
- https://tomcat.apache.org/security-10.html#Fixed_in_Apache_Tomcat_10.1.53
- https://tomcat.apache.org/security-11.html#Fixed_in_Apache_Tomcat_11.0.20
- https://tomcat.apache.org/security-9.html#Fixed_in_Apache_Tomcat_9.0.116
- https://www.herodevs.com/vulnerability-directory/cve-2026-29146
- http://www.openwall.com/lists/oss-security/2026/04/09/24
