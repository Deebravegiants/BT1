# [H] Spring Boot has an Authentication Bypass under Actuator CloudFoundry endpoints

## Summary
Severity: High
Advisory: GHSA-mgvc-8q2h-5pgc
CVE: CVE-2026-22733
CWE: CWE-288
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-mgvc-8q2h-5pgc
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-starter-actuator` — affected >=4.0.0-M1 <4.0.4
- Maven: `org.springframework.boot:spring-boot-starter-actuator` — affected >=3.5.0 <3.5.12
- Maven: `org.springframework.boot:spring-boot-starter-actuator` — affected >=3.4.0
- Maven: `org.springframework.boot:spring-boot-starter-actuator` — affected >=3.0.0
- Maven: `org.springframework.boot:spring-boot-starter-actuator` — affected >=0

## Details
Spring Boot applications with Actuator can be vulnerable to an "Authentication Bypass" vulnerability when an application endpoint that requires authentication is declared under the path used by the CloudFoundry Actuator endpoints. This issue affects Spring Security: from 4.0.0 through 4.0.3, from 3.5.0 through 3.5.11, from 3.4.0 through 3.4.14, from 3.3.0 through 3.3.17, from 2.7.0 through 2.7.31.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22733
- https://github.com/spring-projects/spring-boot
- https://spring.io/security/cve-2026-22733
