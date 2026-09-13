# [M] Spring Boot's random value property source uses a weak PRNG unsuitable for secrets

## Summary
Severity: Medium
Advisory: GHSA-m4x9-hx6x-2c43
CVE: CVE-2026-40975
CWE: CWE-330
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-m4x9-hx6x-2c43
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-cassandra` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.boot:spring-boot-cassandra` — affected >=3.5.0 <3.5.14
- Maven: `org.springframework.boot:spring-boot-cassandra` — affected >=3.4.0
- Maven: `org.springframework.boot:spring-boot-cassandra` — affected >=3.3.0
- Maven: `org.springframework.boot:spring-boot-cassandra` — affected >=0

## Details
Values produced by ${random.value} are not suitable for use as secrets. ${random.uuid} is not affected. ${random.int} and ${random.long} should never be used for secrets as they are numeric values with a predictable range.

Affected: Spring Boot 4.0.0–4.0.5 (fix 4.0.6), 3.5.0–3.5.13 (fix 3.5.14), 3.4.0–3.4.15 (fix 3.4.16), 3.3.0–3.3.18 (fix 3.3.19), 2.7.0–2.7.32 (fix 2.7.33); random value property source / weak PRNG for secrets. Versions that are no longer supported are also affected per vendor advisory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40975
- https://github.com/spring-projects/spring-boot
- https://spring.io/security/cve-2026-40975
