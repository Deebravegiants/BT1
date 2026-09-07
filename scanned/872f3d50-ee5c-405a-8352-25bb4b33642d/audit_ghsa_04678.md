# [M] Spring Framework Open Redirect in Spring MVC and WebFlux

## Summary
Severity: Medium
Advisory: GHSA-h3qp-gqrc-q736
CVE: CVE-2026-41844
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-h3qp-gqrc-q736
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
A Spring MVC or Spring WebFlux application which configures a mapping for "/**" where the view name is not explicitly specified allows an attacker to craft a link resulting in a 302 redirect to an arbitrary external host via the redirect: prefix.

Affected versions:
Spring Framework 7.0.0 through 7.0.7; 6.2.0 through 6.2.18; 6.1.0 through 6.1.27; 5.3.0 through 5.3.48.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41844
- https://github.com/spring-projects/spring-framework/commit/3aaec987651cf82fd4ed7e0ed9b3deddcdf58853
- https://github.com/spring-projects/spring-framework/commit/7add5243b9db13a9f8e765c8ab8545c8e8fe606b
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/releases/tag/v6.2.19
- https://github.com/spring-projects/spring-framework/releases/tag/v7.0.8
- https://spring.io/security/cve-2026-41844
