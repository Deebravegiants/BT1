# [M] Spring Boot's PID file write follows symlinks at predictable default path

## Summary
Severity: Medium
Advisory: GHSA-5368-6h4h-gr29
CVE: CVE-2026-40977
CWE: CWE-59
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-5368-6h4h-gr29
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-cassandra` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.boot:spring-boot-cassandra` — affected >=3.5.0 <3.5.14
- Maven: `org.springframework.boot:spring-boot-cassandra` — affected >=3.4.0
- Maven: `org.springframework.boot:spring-boot-cassandra` — affected >=3.3.0
- Maven: `org.springframework.boot:spring-boot-cassandra` — affected >=0

## Details
When an application is configured to use `ApplicationPidFileWriter`, a local attacker with write access to the PID file's location can corrupt one file on the host each time the application is started.

Affected: Spring Boot 4.0.0–4.0.5 (fix 4.0.6), 3.5.0–3.5.13 (fix 3.5.14), 3.4.0–3.4.15 (fix 3.4.16), 3.3.0–3.3.18 (fix 3.3.19), 2.7.0–2.7.32 (fix 2.7.33); PID file / symlink behavior (`ApplicationPidFileWriter`). Versions that are no longer supported are also affected per vendor advisory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40977
- https://github.com/spring-projects/spring-boot
- https://spring.io/security/cve-2026-40977
