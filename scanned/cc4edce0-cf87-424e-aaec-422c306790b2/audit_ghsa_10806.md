# [H] Spring Boot has an Authentication Bypass under Actuator Health groups paths

## Summary
Severity: High
Advisory: GHSA-8hfc-fq58-r658
CVE: CVE-2026-22731
CWE: CWE-288, CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-8hfc-fq58-r658
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-starter-actuator` — affected >=3.4.0
- Maven: `org.springframework.boot:spring-boot-starter-actuator` — affected >=3.5.0 <3.5.12
- Maven: `org.springframework.boot:spring-boot-starter-actuator` — affected >=4.0.0-M1 <4.0.4

## Details
Spring Boot applications with Actuator can be vulnerable to an "Authentication Bypass" vulnerability when an application endpoint that requires authentication is declared under a specific path, already configured for a Health Group additional path.
This issue affects Spring Boot: from 4.0 before 4.0.3, from 3.5 before 3.5.11, from 3.4 before 3.4.15.
This CVE is similar but not equivalent to CVE-2026-22733, as the conditions for exploit and vulnerable versions are different.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22731
- https://github.com/spring-projects/spring-boot
- https://spring.io/security/cve-2026-22731
