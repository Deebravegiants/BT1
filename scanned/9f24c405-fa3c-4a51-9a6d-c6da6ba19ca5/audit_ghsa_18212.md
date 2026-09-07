# [H] Spring Framework annotation detection mechanism may result in improper authorization

## Summary
Severity: High
Advisory: GHSA-jmp9-x22r-554x
CVE: CVE-2025-41249
CWE: CWE-285, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-jmp9-x22r-554x
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=5.3.0
- Maven: `org.springframework:spring-core` — affected >=6.0.0
- Maven: `org.springframework:spring-core` — affected >=6.2.0 <6.2.11

## Details
The Spring Framework annotation detection mechanism may not correctly resolve annotations on methods within type hierarchies with a parameterized super type with unbounded generics. This can be an issue if such annotations are used for authorization decisions.

Your application may be affected by this if you are using Spring Security's @EnableMethodSecurity feature.

You are not affected by this if you are not using @EnableMethodSecurity or if you do not use security annotations on methods in generic superclasses or generic interfaces.

This CVE is published in conjunction with  CVE-2025-41248 https://spring.io/security/cve-2025-41248 .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41249
- https://github.com/spring-projects/spring-framework/issues/35342
- https://github.com/spring-projects/spring-framework/commit/6d710d482a6785b069e35022e81758953afc21ff
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/releases/tag/v6.2.11
- https://spring.io/security/cve-2025-41249
