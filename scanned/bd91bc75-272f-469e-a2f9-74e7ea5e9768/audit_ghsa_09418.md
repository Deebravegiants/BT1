# [C] Apache Tomcat - Digest authenticator will authenticate any unknown user

## Summary
Severity: Critical
Advisory: GHSA-h6fc-48rj-7qqh
CVE: CVE-2026-43512
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-h6fc-48rj-7qqh
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
Apache Tomcat 9.0.0.M1 to 9.0.117
Older, unsupported versions may also be affected

Description:
When DIGEST authentication was configured, any user not known to the
configured Realm would be authenticated if they presented the password
"null".

Mitigation:
Users of the affected versions should apply one of the following
mitigations:
- Upgrade to Apache Tomcat 11.0.22 or later
- Upgrade to Apache Tomcat 10.1.55 or later
- Upgrade to Apache Tomcat 9.0.118 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43512
- https://github.com/apache/tomcat/commit/3d4d3fae07a6cd9c2eb193c5491001740ec64448
- https://github.com/apache/tomcat/commit/6565a6cb6499e56fe2f34457cec99f9d1c4f39e9
- https://github.com/apache/tomcat/commit/a99c355e8199adbfd67c9a1fffbd85b810b196cd
- https://lists.apache.org/thread/7x09x7o12solvclslw3sz0288xc8wx73
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-9.html
- http://www.openwall.com/lists/oss-security/2026/05/12/8
