# [H] Spring Security annotation detection mechanism has authorization bypass

## Summary
Severity: High
Advisory: GHSA-8v5q-rhf3-jphm
CVE: CVE-2025-41248
CWE: CWE-289, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-8v5q-rhf3-jphm
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=6.4.0 <6.4.10
- Maven: `org.springframework.security:spring-security-core` — affected >=6.5.0 <6.5.4

## Details
The Spring Security annotation detection mechanism may not correctly resolve annotations on methods within type hierarchies with a parameterized super type with unbounded generics. This can be an issue when using @PreAuthorize and other method security annotations, resulting in an authorization bypass.

Your application may be affected by this if you are using Spring Security's @EnableMethodSecurity feature.

You are not affected by this if you are not using @EnableMethodSecurity or if you do not use security annotations on methods in generic superclasses or generic interfaces.

This CVE is published in conjunction with  CVE-2025-41249 https://spring.io/security/cve-2025-41249 .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41248
- https://github.com/spring-projects/spring-security/issues/17898
- https://github.com/spring-projects/spring-security/issues/17899
- https://github.com/spring-projects/spring-security/commit/d0f93fa6d8338149943ae640c53db07de827867f
- https://github.com/spring-projects/spring-security/commit/e5694ac7b5e4394b920c6cab48b7bfbd871f84bd
- https://github.com/spring-projects/spring-security
- https://github.com/spring-projects/spring-security/releases/tag/6.4.10
- https://github.com/spring-projects/spring-security/releases/tag/6.5.4
- https://spring.io/security/cve-2025-41248
