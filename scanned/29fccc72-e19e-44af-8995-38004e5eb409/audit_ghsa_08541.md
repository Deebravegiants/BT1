# [C] Apache Tomcat - HTTP/2 request headers not validated

## Summary
Severity: Critical
Advisory: GHSA-r29c-68gh-xp6x
CVE: CVE-2026-41293
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-r29c-68gh-xp6x
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <9.0.118
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.55
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.22
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <9.0.118
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0-M1 <10.1.55
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0-M1 <11.0.22
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=8.5.0 <9.0.118
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=10.1.0-M1 <10.1.55
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=11.0.0-M1 <11.0.22

## Details
Versions Affected:
Apache Tomcat 11.0.0-M1 to 11.0.21
Apache Tomcat 10.1.0-M1 to 10.1.54
Apache Tomcat 9.0.0.M1 to 9.0.117
Older, unsupported versions may also be affected

Description:
HTTP/2 request headers were not validated which may have triggered
unexpected application behaviour if the application (quite reasonably)
assumed that header value exposed through the Servlet API would be
specification compliant.

Mitigation:
Users of the affected versions should apply one of the following
mitigations:
- Upgrade to Apache Tomcat 11.0.22 or later
- Upgrade to Apache Tomcat 10.1.55 or later
- Upgrade to Apache Tomcat 9.0.118 or later

Credit:
This issue was identified by Dawit Jeong (@dawitngoliath)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41293
- https://github.com/apache/tomcat/commit/19f17a257797e8d139b33ff9c88d362a273be148
- https://github.com/apache/tomcat/commit/1c70480466572c9192ed412ebefcd43fc63137fd
- https://github.com/apache/tomcat/commit/2a2476460e823789f530a22207873ea8cd6eff3b
- https://github.com/apache/tomcat/commit/3915fd27e6810b14ccd21e3d900bd8faef44d3df
- https://github.com/apache/tomcat/commit/57c2b3bfd62792631e1df24cf4237b990a0b36fa
- https://github.com/apache/tomcat/commit/c2925554c677da57390f940d856871e18daaacab
- https://github.com/apache/tomcat/commit/cf9452443bcbf3b1a4b435ef7d624364f1b65ca3
- https://github.com/apache/tomcat/commit/e5cef9618c3f4fd31bd6fb1e83f0f18022280dac
- https://github.com/apache/tomcat/commit/f72a6174ab1f0f5a053435f80448b4f6837fe6d7
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/qwg0q16z7xkb2qrr853wdll5531mvl1r
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-9.html
- http://www.openwall.com/lists/oss-security/2026/05/12/13
