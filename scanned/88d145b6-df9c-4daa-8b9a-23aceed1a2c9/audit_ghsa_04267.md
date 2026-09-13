# [H] Spring HATEOAS heap exhaustion through unbounded internal caching

## Summary
Severity: High
Advisory: GHSA-439x-6767-44cv
CVE: CVE-2026-41007
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-439x-6767-44cv
Type: github-advisory

## Affected
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=3.0.0 <3.0.4
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=2.5.0 <2.5.3
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=2.3.0
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=0
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=2.4.0

## Details
Spring HATEOAS maintains an unbounded static cache of StringLinkRelation instances keyed on attacker-supplied strings.

Affected versions:
Spring HATEOAS 1.5.0 through 1.5.6; 2.3.0 through 2.3.4; 2.4.0 through 2.4.1; 2.5.0 through 2.5.2; 3.0.0 through 3.0.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41007
- https://github.com/spring-projects/spring-hateoas/issues/2514
- https://github.com/spring-projects/spring-hateoas/issues/2518
- https://github.com/spring-projects/spring-hateoas/issues/2519
- https://github.com/spring-projects/spring-hateoas/commit/668fd3282e1c7ffc817499b4b3d85d3aa21c0c2e
- https://github.com/spring-projects/spring-hateoas/commit/6b6622c92fd06d028a1d4522addf0e214c079f29
- https://github.com/spring-projects/spring-hateoas/commit/b0a408f4b372b5287e23ec00260808958953496c
- https://github.com/spring-projects/spring-hateoas
- https://github.com/spring-projects/spring-hateoas/releases/tag/2.5.3
- https://github.com/spring-projects/spring-hateoas/releases/tag/3.0.4
- https://spring.io/security/cve-2026-41007
