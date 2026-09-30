# [M] Spring Boot: Predictable Temp Directory in Artemis Auto-configuration

## Summary
Severity: Medium
Advisory: GHSA-ggg2-9786-hwc8
CVE: CVE-2026-41001
CWE: CWE-377
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-ggg2-9786-hwc8
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-autoconfigure` — affected >=4.0.0 <4.0.7
- Maven: `org.springframework.boot:spring-boot-autoconfigure` — affected >=3.5.0 <3.5.15
- Maven: `org.springframework.boot:spring-boot-autoconfigure` — affected >=3.4.0
- Maven: `org.springframework.boot:spring-boot-autoconfigure` — affected >=3.3.0
- Maven: `org.springframework.boot:spring-boot-autoconfigure` — affected >=2.7.0

## Details
Spring Boot's ArtemisEmbeddedConfigurationFactory uses a fixed, static path for the embedded Artemis message broker's data directory when no explicit path is configured. A local attacker on the same host can pre-create this predictable directory or place a symlink before the application starts.

Affected versions:
Spring Boot 4.0.0 through 4.0.6; 3.5.0 through 3.5.14; 3.4.0 through 3.4.16; 3.3.0 through 3.3.19; 2.7.0 through 2.7.33.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41001
- https://github.com/spring-projects/spring-boot/commit/4218bd76e934e5cf9e3fd3997c67b8a6b0d0c111
- https://github.com/spring-projects/spring-boot
- https://spring.io/security/cve-2026-41001
