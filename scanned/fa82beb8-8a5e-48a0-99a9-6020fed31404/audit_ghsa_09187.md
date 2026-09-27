# [C] Apache Tomcat - Security constraints not correctly applied

## Summary
Severity: Critical
Advisory: GHSA-5m62-pw8w-7w9f
CVE: CVE-2026-43515
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-5m62-pw8w-7w9f
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
When multiple security constraints defined an HTTP method constraint for
the same extension pattern, only the first method constraint was applied.

Mitigation:
Users of the affected versions should apply one of the following
mitigations:
- Upgrade to Apache Tomcat 11.0.22 or later
- Upgrade to Apache Tomcat 10.1.55 or later
- Upgrade to Apache Tomcat 9.0.118 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43515
- https://github.com/apache/tomcat/commit/276087d9c7abbcecc6c4fb4e4b08cf64780c6e36
- https://github.com/apache/tomcat/commit/c621317382682206fb58ab92ebd3e1b6fdd10ce9
- https://github.com/apache/tomcat/commit/db919ff9912b4d61d1b702a1342b8bde39270031
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/746nxfxod0wsocxtmv8pb8nkgmwpc6bb
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-9.html
- http://www.openwall.com/lists/oss-security/2026/05/12/11
