# [H] Apache Tomcat - WebSocket authentication header exposure

## Summary
Severity: High
Advisory: GHSA-fv25-8xcx-gqjc
CVE: CVE-2026-42498
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-fv25-8xcx-gqjc
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=0 <9.0.118
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.55
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.22
- Maven: `org.apache.tomcat:tomcat` — affected >=0 <9.0.118
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0-M1 <10.1.55
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0-M1 <11.0.22
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=0 <9.0.118
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0-M1 <10.1.55
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=11.0.0-M1 <11.0.22

## Details
Versions Affected:
Apache Tomcat 11.0.0-M1 to 11.0.21
Apache Tomcat 10.1.0-M1 to 10.1.54
Apache Tomcat 9.0.2 to 9.0.117
Older, unsupported versions may also be affected

Description:
If a WebSocket request was redirected after authentication, Tomcat's
WebSocket client would present the most recent authentication header to
the redirect target host.

Mitigation:
Users of the affected versions should apply one of the following
mitigations:
- Upgrade to Apache Tomcat 11.0.22 or later
- Upgrade to Apache Tomcat 10.1.55 or later
- Upgrade to Apache Tomcat 9.0.118 or later

Credit:
This issue was identified by lokerxx

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42498
- https://github.com/apache/tomcat/commit/169d725788ea6aec217ecac70fe4161c837ba423
- https://github.com/apache/tomcat/commit/6cbe274592ef2d11607b5b188e1df649de52f8d5
- https://github.com/apache/tomcat/commit/b7b173694d588ddcfa432f079baf763cbbbaa5c4
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/n61zwf75jrv09rz90j4jssncm244bwdb
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-9.html
- http://www.openwall.com/lists/oss-security/2026/05/12/14
