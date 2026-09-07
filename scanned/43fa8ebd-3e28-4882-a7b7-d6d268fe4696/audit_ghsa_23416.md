# [M] Improper Neutralization of Input During Web Page Generation in Spring Framework

## Summary
Severity: Medium
Advisory: GHSA-xjrf-8x4f-43h4
CVE: CVE-2013-6430
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-xjrf-8x4f-43h4
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-web` — affected >=0 <3.2.2.RELEASE

## Details
The JavaScriptUtils.javaScriptEscape method in web/util/JavaScriptUtils.java in Spring MVC in Spring Framework before 3.2.2 does not properly escape certain characters, which allows remote attackers to conduct cross-site scripting (XSS) attacks via a (1) line separator or (2) paragraph separator Unicode character or (3) left or (4) right angle bracket.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6430
- https://github.com/spring-projects/spring-framework/issues/14617
- https://github.com/spring-projects/spring-framework/commit/7a7df6637478607bef0277bf52a4e0a03e20a248
- https://github.com/spring-projects/spring-framework/commit/9982b4c01a8c7be0961e58b58ed83731c40449ff
- https://github.com/spring-projects/spring-framework/commit/f5c9fe69a444607af667911bd4c5074b5b073e7b
- https://github.com/spring-projects/spring-framework
- https://jira.spring.io/browse/SPR-9983?redirect=false
- https://spring.io/security/cve-2013-6430
