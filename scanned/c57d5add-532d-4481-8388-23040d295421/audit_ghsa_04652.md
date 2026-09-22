# [H] Spring HATEOAS Collection+JSON/UBER deserializers do not honor Jackson configuration

## Summary
Severity: High
Advisory: GHSA-7fxc-486f-32q9
CVE: CVE-2026-41006
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-7fxc-486f-32q9
Type: github-advisory

## Affected
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=3.0.0 <3.0.4
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=2.5.0 <2.5.3
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=2.3.0
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=0
- Maven: `org.springframework.hateoas:spring-hateoas` — affected >=2.4.0

## Details
Spring HATEOAS's internal PropertyUtils.createObjectFromProperties method, used by the Collection+JSON and UBER media type deserializers, performs bean property binding via reflection without consulting Jackson access-control annotations.

Affected versions:
Spring HATEOAS 1.5.0 through 1.5.6; 2.3.0 through 2.3.4; 2.4.0 through 2.4.1; 2.5.0 through 2.5.2; 3.0.0 through 3.0.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41006
- https://github.com/spring-projects/spring-hateoas/issues/2515
- https://github.com/spring-projects/spring-hateoas/issues/2516
- https://github.com/spring-projects/spring-hateoas/issues/2517
- https://github.com/spring-projects/spring-hateoas/commit/2c127edd741e43e6e6f06f4081af92d400209990
- https://github.com/spring-projects/spring-hateoas/commit/87d73a7af52d70e51823f44a67371b7a8a54b7c1
- https://github.com/spring-projects/spring-hateoas/commit/d8050eedca1c92e1839f18ec1f7e0eecfb511389
- https://github.com/spring-projects/spring-hateoas
- https://github.com/spring-projects/spring-hateoas/releases/tag/2.5.3
- https://github.com/spring-projects/spring-hateoas/releases/tag/3.0.4
- https://spring.io/security/cve-2026-41006
