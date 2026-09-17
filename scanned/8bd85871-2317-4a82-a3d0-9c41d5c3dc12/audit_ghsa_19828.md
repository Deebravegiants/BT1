# [C] Apache Tomcat: Potential RCE and/or information disclosure and/or information corruption with partial PUT

## Summary
Severity: Critical
Advisory: GHSA-83qj-6fr2-vhqg
CVE: CVE-2025-24813
CWE: CWE-44, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-83qj-6fr2-vhqg
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=11.0.0-M1 <11.0.3
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0-M1 <10.1.35
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0.M1 <9.0.99
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.3
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.35
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.99
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.0
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0

## Details
Path Equivalence: 'file.Name' (Internal Dot) leading to Remote Code Execution and/or Information disclosure and/or malicious content added to uploaded files via write enabled Default Servlet in Apache Tomcat.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.2, from 10.1.0-M1 through 10.1.34, from 9.0.0.M1 through 9.0.98. The following versions were EOL at the time the CVE was created but are known to be affected: 8.5.0 though 8.5.100. Other, older, EOL versions may also be affected.

If all of the following were true, a malicious user was able to view security sensitive files and/or inject content into those files:
- writes enabled for the default servlet (disabled by default)
- support for partial PUT (enabled by default)
- a target URL for security sensitive uploads that was a sub-directory of a target URL for public uploads
- attacker knowledge of the names of security sensitive files being uploaded
- the security sensitive files also being uploaded via partial PUT

If all of the following were true, a malicious user was able to perform remote code execution:
- writes enabled for the default servlet (disabled by default)
- support for partial PUT (enabled by default)
- application was using Tomcat's file based session persistence with the default storage location
- application included a library that may be leveraged in a deserialization attack

Users are recommended to upgrade to version 11.0.3, 10.1.35 or 9.0.99, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24813
- https://github.com/apache/tomcat/commit/0a668e0c27f2b7ca0cc7c6eea32253b9b5ecb29c
- https://github.com/apache/tomcat/commit/eb61aade8f8daccaecabf07d428b877975622f72
- https://github.com/apache/tomcat/commit/f6c01d6577cf9a1e06792be47e623d36acc3b5dc
- https://github.com/absholi7ly/POC-CVE-2025-24813/blob/main/README.md
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/j5fkjv2k477os90nczf2v9l61fb0kkgq
- https://lists.debian.org/debian-lts-announce/2025/04/msg00003.html
- https://security.netapp.com/advisory/ntap-20250321-0001
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-24813
- https://www.vicarius.io/vsociety/posts/cve-2025-24813-detect-apache-tomcat-rce
- https://www.vicarius.io/vsociety/posts/cve-2025-24813-mitigate-apache-tomcat-rce
- https://www.vicarius.io/vsociety/posts/cve-2025-24813-tomcat-detect-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-24813-tomcat-mitigation-vulnerability
- http://www.openwall.com/lists/oss-security/2025/03/10/5
