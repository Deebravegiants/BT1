# [H] Apache Tomcat Vulnerable to Relative Path Traversal

## Summary
Severity: High
Advisory: GHSA-wmwf-9ccg-fff5
CVE: CVE-2025-55752
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-27
Source: https://github.com/advisories/GHSA-wmwf-9ccg-fff5
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0-M1 <11.0.11
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0-M1 <10.1.45
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0-M11 <9.0.109
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.6
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=11.0.0-M1 <11.0.11
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.1.0-M1 <10.1.45
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0-M11 <9.0.109
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.5.6
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.11
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.45
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0-M11 <9.0.109
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.6

## Details
The fix for bug 60013 introduced a regression where the rewritten URL was normalized before it was decoded. This introduced the possibility that, for rewrite rules that rewrite query parameters to the URL, an attacker could manipulate the request URI to bypass security constraints including the protection for /WEB-INF/ and /META-INF/. If PUT requests were also enabled then malicious files could be uploaded leading to remote code execution. PUT requests are normally limited to trusted users and it is considered unlikely that PUT requests would be enabled in conjunction with a rewrite that manipulated the URI.



This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.10, from 10.1.0-M1 through 10.1.44, from 9.0.0.M11 through 9.0.108.

The following versions were EOL at the time the CVE was created but are  known to be affected: 8.5.6 though 8.5.100. Other, older, EOL versions may also be affected. Users are recommended to upgrade to version 11.0.11 or later, 10.1.45 or later or 9.0.109 or later, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-55752
- https://github.com/apache/tomcat/commit/130d36d8492ef9e4eb22952c17c92423cb35fd06
- https://github.com/apache/tomcat/commit/b5042622b8b78340ae65403c55dcb9c7416924df
- https://github.com/apache/tomcat/commit/fec06c610ed7466b401e29cc567a58aee5ed826a
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/n05kjcwyj1s45ovs8ll1qrrojhfb1tog
- https://tomcat.apache.org/security-10.html#Fixed_in_Apache_Tomcat_10.1.45
- https://tomcat.apache.org/security-11.html#Fixed_in_Apache_Tomcat_11.0.11
- https://tomcat.apache.org/security-9.html#Fixed_in_Apache_Tomcat_9.0.109
- https://www.vicarius.io/vsociety/posts/cve-2025-55752-detect-apache-tomcat-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-55752-mitigate-apache-tomcat-vulnerability
- http://www.openwall.com/lists/oss-security/2025/10/27/4
