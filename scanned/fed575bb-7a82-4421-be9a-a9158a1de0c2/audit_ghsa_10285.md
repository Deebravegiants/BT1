# [C] Spring Boot's default security filter chain has no authorization rule with Actuator but without Health

## Summary
Severity: Critical
Advisory: GHSA-8v8j-3hxp-93wr
CVE: CVE-2026-40976
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-8v8j-3hxp-93wr
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot` — affected >=4.0.0 <4.0.6

## Details
In certain circumstances, Spring Boot's default web security is ineffective allowing unauthorized access to all endpoints. For an application to be vulnerable, it must: be a servlet-based web application; have no Spring Security configuration of its own and rely on the default web security filter chain; depend on spring-boot-actuator-autoconfigure; not depend on spring-boot-health. If any of the above does not apply, the application is not vulnerable.

Affected: Spring Boot 4.0.0–4.0.5; upgrade to 4.0.6 or later per vendor advisory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40976
- https://github.com/spring-projects/spring-boot
- https://spring.io/security/cve-2026-40976
