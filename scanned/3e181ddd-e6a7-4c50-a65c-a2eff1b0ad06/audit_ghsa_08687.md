# [H] Apache Tomcat: Unbounded read in WebDAV LOCK and  PROPFIND handling

## Summary
Severity: High
Advisory: GHSA-gx5v-xp9w-j4cg
CVE: CVE-2026-41284
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-gx5v-xp9w-j4cg
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
No limit was enforced on the request body for WebDAV LOCK or PROPFIND
requests which were available to unauthenticated users.

Mitigation:
Users of the affected versions should apply one of the following
mitigations:
- Upgrade to Apache Tomcat 11.0.22 or later
- Upgrade to Apache Tomcat 10.1.55 or later
- Upgrade to Apache Tomcat 9.0.118 or later

Credit:
This issue was identified by Dariusz Gońda

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41284
- https://github.com/apache/tomcat/commit/17dacd9aa48628da2eba37a9ab743c0b6c71685c
- https://github.com/apache/tomcat/commit/a96fffd18487a29c0a30d36f00cb2b2d91f6d42c
- https://github.com/apache/tomcat/commit/b3d1c1c239142e806be0b7329d304b94a58913ed
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/2nvqjr7ovjmvx2vbhb7s61ycd5msc8qc
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-9.html
- http://www.openwall.com/lists/oss-security/2026/05/12/12
