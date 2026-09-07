# [C] Apache Tomcat: CLIENT_CERT authentication does not fail as expected

## Summary
Severity: Critical
Advisory: GHSA-95jq-rwvf-vjx4
CVE: CVE-2026-29145
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-95jq-rwvf-vjx4
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-coyote-ffm` — affected >=9.0.83 <9.0.116
- Maven: `org.apache.tomcat:tomcat-coyote-ffm` — affected >=10.1.0-M7 <10.1.53
- Maven: `org.apache.tomcat:tomcat-coyote-ffm` — affected >=11.0.0-M1 <11.0.20
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.83 <9.0.116
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0-M7 <10.1.53
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0-M1 <11.0.20

## Details
CLIENT_CERT authentication does not fail as expected for some scenarios when soft fail is disabled vulnerability in Apache Tomcat, Apache Tomcat Native.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.18, from 10.1.0-M7 through 10.1.52, from 9.0.83 through 9.0.115; Apache Tomcat Native: from 1.1.23 through 1.1.34, from 1.2.0 through 1.2.39, from 1.3.0 through 1.3.6, from 2.0.0 through 2.0.13.

Users are recommended to upgrade to version Tomcat Native 1.3.7 or 2.0.14 and Tomcat 11.0.20, 10.1.53 and 9.0.116, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-29145
- https://github.com/apache/tomcat/commit/721591f7bff424c693f26adc18ae9b9abac3655b
- https://github.com/apache/tomcat/commit/d1406df5ae0326f39f54c3f64ac30d8fca55cd5b
- https://github.com/apache/tomcat/commit/fe26667cd2385045ac73f4dea086cc9971209b90
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/yz5fxmhd2j43wgqykssdo7kltws57jfz
- https://tomcat.apache.org/security-10.html#Fixed_in_Apache_Tomcat_10.1.53
- https://tomcat.apache.org/security-11.html#Fixed_in_Apache_Tomcat_11.0.20
- https://tomcat.apache.org/security-9.html#Fixed_in_Apache_Tomcat_9.0.116
- http://www.openwall.com/lists/oss-security/2026/04/09/23
