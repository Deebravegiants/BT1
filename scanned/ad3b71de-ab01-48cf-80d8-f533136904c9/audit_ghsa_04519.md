# [M] Spring Framework Escalation via Session Fixation in WebFlux

## Summary
Severity: Medium
Advisory: GHSA-4hfh-6x8g-gwpp
CVE: CVE-2026-41839
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-4hfh-6x8g-gwpp
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webflux` — affected >=7.0.0 <7.0.8
- Maven: `org.springframework:spring-webflux` — affected >=6.2.0 <6.2.19
- Maven: `org.springframework:spring-webflux` — affected >=6.1.0
- Maven: `org.springframework:spring-webflux` — affected >=0

## Details
A WebFlux application with a compromised subdomain (for example, compromised via cross-site scripting (XSS)) is vulnerable to an escalation attack exchanging a known session ID for that of an authenticated user.

Affected versions:
Spring Framework 7.0.0 through 7.0.7; 6.2.0 through 6.2.18; 6.1.0 through 6.1.27; 5.3.0 through 5.3.48.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41839
- https://github.com/spring-projects/spring-framework/issues/36742
- https://github.com/spring-projects/spring-framework/issues/36743
- https://github.com/spring-projects/spring-framework/commit/b8ddd2c690fe3f00bb5e3d9f913a37504aab49a0
- https://github.com/spring-projects/spring-framework/commit/d72da90d3a562632e2b565113813f7b4a31f8717
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/releases/tag/v6.2.19
- https://github.com/spring-projects/spring-framework/releases/tag/v7.0.8
- https://spring.io/security/cve-2026-41839
