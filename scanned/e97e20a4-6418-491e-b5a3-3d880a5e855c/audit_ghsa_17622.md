# [M] Apache Tomcat installer for Windows has an untrusted search path vulnerability

## Summary
Severity: Medium
Advisory: GHSA-42wg-hm62-jcwg
CVE: CVE-2025-49124
CWE: CWE-426
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-42wg-hm62-jcwg
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.8
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0 <10.1.42
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.23 <9.0.106
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0-M1 <11.0.8
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0 <10.1.42
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.23 <9.0.106
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=11.0.0-M1 <11.0.8
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0 <10.1.42
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.23 <9.0.106

## Details
Untrusted Search Path vulnerability in Apache Tomcat installer for Windows. During installation, the Tomcat installer for Windows used icacls.exe without specifying a full path.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.7, from 10.1.0 through 10.1.41, from 9.0.23 through 9.0.105.

Users are recommended to upgrade to version 11.0.8, 10.1.42 or 9.0.106, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49124
- https://github.com/apache/tomcat/commit/28726cc2e63bed68771f5eb0f65a78dc7080571823
- https://github.com/apache/tomcat/commit/c56456cda8151c9504dfb7985700824559d769a7
- https://github.com/apache/tomcat/commit/e0e07812224d327a321babb554f5a5758d30cc49
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/lnow7tt2j6hb9kcpkggx32ht6o90vqzv
- https://tomcat.apache.org/security-10.html#Fixed_in_Apache_Tomcat_10.1.42
- https://tomcat.apache.org/security-11.html#Fixed_in_Apache_Tomcat_11.0.8
- https://tomcat.apache.org/security-9.html#Fixed_in_Apache_Tomcat_9.0.106
- http://www.openwall.com/lists/oss-security/2025/06/16/3
