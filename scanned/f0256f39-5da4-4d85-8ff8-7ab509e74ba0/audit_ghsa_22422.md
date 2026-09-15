# [M] Spring Framework and Spring Security vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Medium
Advisory: GHSA-f866-m9mv-2xr3
CVE: CVE-2011-2894
CWE: CWE-502
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f866-m9mv-2xr3
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=3.0.0 <3.0.6
- Maven: `org.springframework.security:spring-security-core` — affected >=3.0.0 <3.0.6
- Maven: `org.springframework.security:spring-security-core` — affected >=2.0.0 <2.0.7

## Details
Spring Framework 3.0.0 through 3.0.5, Spring Security 3.0.0 through 3.0.5 and 2.0.0 through 2.0.6, and possibly other versions deserialize objects from untrusted sources, which allows remote attackers to bypass intended security restrictions and execute untrusted code by (1) serializing a java.lang.Proxy instance and using InvocationHandler, or (2) accessing internal AOP interfaces, as demonstrated using deserialization of a DefaultListableBeanFactory instance to execute arbitrary commands via the java.lang.Runtime class.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2894
- https://github.com/spring-projects/spring-framework/commit/070a723ef2c886770a063eb9a67f84f74e06edfb
- https://exchange.xforce.ibmcloud.com/vulnerabilities/69687
- https://github.com/spring-projects/spring-framework
- https://web.archive.org/web/20120307233721/http://www.springsource.com/security/cve-2011-2894
- http://osvdb.org/75263
- http://securityreason.com/securityalert/8405
- http://www.redhat.com/support/errata/RHSA-2011-1334.html
- http://www.securityfocus.com/archive/1/519593/100/0/threaded
- http://www.securityfocus.com/bid/49536
- http://www.springsource.com/security/cve-2011-2894
