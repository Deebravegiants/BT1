# [M] Spring Framework Information Disclosure via Static Resource Cache in Spring MVC and WebFlux

## Summary
Severity: Medium
Advisory: GHSA-mq64-j8f9-9gcj
CVE: CVE-2026-41841
CWE: CWE-524
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-mq64-j8f9-9gcj
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webmvc` — affected >=7.0.0 <7.0.8
- Maven: `org.springframework:spring-webflux` — affected >=7.0.0 <7.0.8
- Maven: `org.springframework:spring-webmvc` — affected >=6.2.0 <6.2.19
- Maven: `org.springframework:spring-webflux` — affected >=6.2.0 <6.2.19
- Maven: `org.springframework:spring-webmvc` — affected >=6.1.0
- Maven: `org.springframework:spring-webflux` — affected >=6.1.0
- Maven: `org.springframework:spring-webmvc` — affected >=0
- Maven: `org.springframework:spring-webflux` — affected >=0

## Details
Spring MVC and WebFlux applications are vulnerable to Information Disclosure attacks when resolving static resources.

Affected versions:
Spring Framework 7.0.0 through 7.0.7; 6.2.0 through 6.2.18; 6.1.0 through 6.1.27; 5.3.0 through 5.3.48.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41841
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/releases/tag/v6.2.19
- https://github.com/spring-projects/spring-framework/releases/tag/v7.0.8
- https://spring.io/security/cve-2026-41841
