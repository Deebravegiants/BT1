# [H] Apache Tomcat vulnerable to Insertion of Sensitive Information into Log File

## Summary
Severity: High
Advisory: GHSA-x4m4-345f-5h5g
CVE: CVE-2026-34487
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-x4m4-345f-5h5g
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=9.0.13 <9.0.117
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=10.1.0-M1 <10.1.54
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=11.0.0-M1 <11.0.21
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.13 <9.0.117
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0-M1 <10.1.54
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0-M1 <11.0.21
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.13 <9.0.117
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.54
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.21

## Details
Insertion of Sensitive Information into Log File vulnerability in the cloud membership for clustering component of Apache Tomcat exposed the Kubernetes bearer token.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.20, from 10.1.0-M1 through 10.1.53, from 9.0.13 through 9.0.116.

Users are recommended to upgrade to version 11.0.21, 10.1.54 or 9.0.117, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34487
- https://github.com/apache/tomcat/commit/301bc6efbf72feb14dacfdfa3f50372182736150
- https://github.com/apache/tomcat/commit/5eff2a773b8b728083e5195b3183df1b9e12a03d
- https://github.com/apache/tomcat/commit/f593292a082e5ef9336a8db2b4b522f7f3e36976
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/4xpkwolpkrj8v5xzp5nyovtlqp3y850h
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-9.html
- http://www.openwall.com/lists/oss-security/2026/04/09/28
