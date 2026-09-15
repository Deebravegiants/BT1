# [M] Spring Framework Predictable Session ID in WebSocket Module

## Summary
Severity: Medium
Advisory: GHSA-q723-847q-5g8g
CVE: CVE-2026-41838
CWE: CWE-330
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-q723-847q-5g8g
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-websocket` — affected >=7.0.0 <7.0.8
- Maven: `org.springframework:spring-websocket` — affected >=6.2.0 <6.2.19
- Maven: `org.springframework:spring-websocket` — affected >=6.1.0
- Maven: `org.springframework:spring-websocket` — affected >=0

## Details
IDs for WebSocket sessions in the spring-websocket module are not cryptographically unpredictable, which may be possible to exploit in combination with inadequate authorization rules.

Affected versions:
Spring Framework 7.0.0 through 7.0.7; 6.2.0 through 6.2.18; 6.1.0 through 6.1.27; 5.3.0 through 5.3.48.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41838
- https://github.com/spring-projects/spring-framework/issues/36740
- https://github.com/spring-projects/spring-framework/commit/a42a6e0c6ac64eb18954729ca5e3fe64b05a39b5
- https://github.com/spring-projects/spring-framework/commit/bff98999056fc29b573ff47ad2433462eb52833c
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/releases/tag/v6.2.19
- https://github.com/spring-projects/spring-framework/releases/tag/v7.0.8
- https://spring.io/security/cve-2026-41838
