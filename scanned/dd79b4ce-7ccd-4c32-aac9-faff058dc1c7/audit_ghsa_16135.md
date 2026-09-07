# [M] Apache Tomcat - XSS in generated JSPs

## Summary
Severity: Medium
Advisory: GHSA-f632-9449-3j4w
CVE: CVE-2024-52318
CWE: CWE-326
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-f632-9449-3j4w
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-jasper` — affected >=11.0.0 <11.0.1
- Maven: `org.apache.tomcat:tomcat-jasper` — affected >=10.1.31 <10.1.32
- Maven: `org.apache.tomcat.embed:tomcat-embed-jasper` — affected >=9.0.96 <9.0.97
- Maven: `org.apache.tomcat.embed:tomcat-embed-jasper` — affected >=11.0.0 <11.0.1
- Maven: `org.apache.tomcat.embed:tomcat-embed-jasper` — affected >=10.1.31 <10.1.32
- Maven: `org.apache.tomcat:tomcat-jasper` — affected >=9.0.96 <9.0.97
- Maven: `org.apache.tomcat:tomcat` — affected >=11.0.0 <11.0.1
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.31 <10.1.32
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.96 <9.0.97

## Details
# Description:
The fix for improvement 69333 caused pooled JSP tags not to be released after use which in turn could cause output of some tags not to escaped as expected. This unescaped output could lead to XSS.

# Versions Affected:
- Apache Tomcat 11.0.0
- Apache Tomcat 10.1.31
- Apache Tomcat 9.0.96

# Mitigation:
Users of the affected versions should apply one of the following
mitigations:
- Upgrade to Apache Tomcat 11.0.1 or later
- Upgrade to Apache Tomcat 10.1.33 or later
Note: 10.1.32 was not released
- Upgrade to Apache Tomcat 9.0.97 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52318
- https://github.com/apache/tomcat/commit/8d1fc4733a06d1a03b9d644c57010f2ec5f0df38
- https://github.com/apache/tomcat/commit/9813c5dd3259183f659bbb83312a5cf673cc1ebf
- https://github.com/apache/tomcat/commit/be8e32143a3159e78fe5463d09bb8e1b33bf2b1f
- https://bz.apache.org/bugzilla/show_bug.cgi?id=69333
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/co243cw1nlh6p521c5265cm839wkqdp9
- https://security.netapp.com/advisory/ntap-20250131-0009
- http://www.openwall.com/lists/oss-security/2024/11/18/4
