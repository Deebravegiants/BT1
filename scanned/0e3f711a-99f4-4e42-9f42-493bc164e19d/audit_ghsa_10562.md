# [H] Apache Tomcat Missing Encryption of Sensitive Data vulnerability

## Summary
Severity: High
Advisory: GHSA-69r9-qgr7-g2wj
CVE: CVE-2026-34486
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-69r9-qgr7-g2wj
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=11.0.20 <11.0.21
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=10.1.53 <10.1.54
- Maven: `org.apache.tomcat:tomcat-tribes` — affected >=9.0.116 <9.0.117
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.20 <11.0.21
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.53 <10.1.54
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.116 <9.0.117

## Details
Missing Encryption of Sensitive Data vulnerability in Apache Tomcat due to the fix for CVE-2026-29146 allowing the bypass of the EncryptInterceptor.

This issue affects Apache Tomcat: 11.0.20, 10.1.53, 9.0.116.

Users are recommended to upgrade to version 11.0.21, 10.1.54 or 9.0.117, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34486
- https://github.com/apache/tomcat/commit/1fab40ccc752e22639eccfe290d5624afad7eccd
- https://github.com/apache/tomcat/commit/55f3eb9148233054fccfdf761141c6894a050be1
- https://github.com/apache/tomcat/commit/776e12b3e2b0b4507b8a3b62c187ceb0b74bf418
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/9510k5p5zdvt9pkkgtyp85mvwxo2qrly
- https://tomcat.apache.org/security-10.html#Fixed_in_Apache_Tomcat_10.1.54
- https://tomcat.apache.org/security-11.html#Fixed_in_Apache_Tomcat_11.0.21
- https://tomcat.apache.org/security-9.html#Fixed_in_Apache_Tomcat_9.0.117
- https://www.herodevs.com/vulnerability-directory/cve-2026-34486
- https://www.vicarius.io/vsociety/posts/cve-2026-34486-detection-script-rce-on-apache-tomcat
- https://www.vicarius.io/vsociety/posts/cve-2026-34486-mitigation-script-rce-on-apache-tomcat
