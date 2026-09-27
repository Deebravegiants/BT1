# [H] Apache Tomcat has an Improper Encoding or Escaping of Output vulnerability in the JsonAccessLogValve

## Summary
Severity: High
Advisory: GHSA-rv64-5gf8-9qq8
CVE: CVE-2026-34483
CWE: CWE-116
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-rv64-5gf8-9qq8
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.40 <9.0.116
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0-M1 <10.1.54
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=11.0.0-M1 <11.0.21
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.40 <9.0.116
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0-M1 <10.1.54
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0-M1 <11.0.21
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.40 <9.0.116
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.54
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.21

## Details
Improper Encoding or Escaping of Output vulnerability in the JsonAccessLogValve component of Apache Tomcat.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.20, from 10.1.0-M1 through 10.1.53, from 9.0.40 through 9.0.116.

Users are recommended to upgrade to version 11.0.21, 10.1.54 or 9.0.117 , which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34483
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/j1w7304yonlr8vo1tkb5nfs7od1y228b
- http://www.openwall.com/lists/oss-security/2026/04/09/26
