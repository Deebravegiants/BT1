# [H] Apache Tomcat - DoS in multipart upload

## Summary
Severity: High
Advisory: GHSA-h3gc-qfqq-6h8f
CVE: CVE-2025-48988
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-h3gc-qfqq-6h8f
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=11.0.0-M1 <11.0.8
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0-M1 <10.1.42
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0.M1 <9.0.106
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.8
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.42
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.106
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.0
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0

## Details
Allocation of Resources Without Limits or Throttling vulnerability in Apache Tomcat.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.7, from 10.1.0-M1 through 10.1.41, from 9.0.0.M1 through 9.0.105. The following versions were EOL at the time the CVE was created but are known to be affected: 8.5.0 though 8.5.100. Other, older, EOL versions may also be affected.

Users are recommended to upgrade to version 11.0.8, 10.1.42 or 9.0.106, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48988
- https://github.com/apache/tomcat/commit/2b0ab14fb55d4edc896e5f1817f2ab76f714ae5e
- https://github.com/apache/tomcat/commit/cdde8e655bc1c5c60a07efd216251d77c52fd7f6
- https://github.com/apache/tomcat/commit/ee8042ffce4cb9324dfd79efda5984f37bbb6910
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/nzkqsok8t42qofgqfmck536mtyzygp18
- https://lists.debian.org/debian-lts-announce/2025/07/msg00009.html
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-9.html
- http://www.openwall.com/lists/oss-security/2025/06/16/1
