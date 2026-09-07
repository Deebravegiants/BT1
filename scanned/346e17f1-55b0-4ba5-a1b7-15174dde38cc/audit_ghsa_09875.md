# [M] Spring Boot's RabbitMQ auto-configuration doesn't perform hostname verification when connecting to the RabbitMQ broker

## Summary
Severity: Medium
Advisory: GHSA-9vc8-qppq-wvxc
CVE: CVE-2026-40971
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-9vc8-qppq-wvxc
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-rabbitmq` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.boot:spring-boot-rabbitmq` — affected >=3.5.0 <3.5.14

## Details
When configured to use an SSL bundle, Spring Boot's RabbitMQ auto-configuration does not perform hostname verification when connecting to the RabbitMQ broker.

Affected: Spring Boot 4.0.0–4.0.5 (fix 4.0.6), 3.5.0–3.5.13 (fix 3.5.14) per vendor advisory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40971
- https://github.com/spring-projects/spring-boot
- https://spring.io/security/cve-2026-40971
