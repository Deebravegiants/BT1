# [H] Apache Tomcat: Configured cipher preference order not preserved

## Summary
Severity: High
Advisory: GHSA-69cc-cv78-qc8g
CVE: CVE-2026-29129
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-69cc-cv78-qc8g
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=9.0.114 <9.0.116
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=10.1.51 <10.1.53
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=11.0.16 <11.0.20
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.114 <9.0.116
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.51 <10.1.53
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.16 <11.0.20
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.114 <9.0.116
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.51 <10.1.53
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.16 <11.0.20

## Details
Configured cipher preference order not preserved vulnerability in Apache Tomcat.

This issue affects Apache Tomcat: from 11.0.16 through 11.0.18, from 10.1.51 through 10.1.52, from 9.0.114 through 9.0.115.

Users are recommended to upgrade to version 11.0.20, 10.1.53 or 9.0.116, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-29129
- https://github.com/apache/tomcat/commit/5cfa876d73f1ff5f4dc8309c4320f684cbeff74e
- https://github.com/apache/tomcat/commit/6db238562ec36ab1106db4d04843f8b33e7a0c06
- https://github.com/apache/tomcat/commit/8d69b33764dba81dce89e3a768de6093a35620ae
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/r4h1t6f8xhxsxfm6c2z5cprolsosho3f
- https://tomcat.apache.org/security-10.html#Fixed_in_Apache_Tomcat_10.1.53
- https://tomcat.apache.org/security-11.html#Fixed_in_Apache_Tomcat_11.0.20
- https://tomcat.apache.org/security-9.html#Fixed_in_Apache_Tomcat_9.0.116
- http://www.openwall.com/lists/oss-security/2026/04/09/22
