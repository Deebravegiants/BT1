# [M] Spring Boot's Elasticsearch auto-configuration doesn't perform hostname verification when connecting to the Elasticsearch server.

## Summary
Severity: Medium
Advisory: GHSA-c96x-rpm4-349p
CVE: CVE-2026-40970
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-c96x-rpm4-349p
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-elasticsearch` — affected >=4.0.0 <4.0.6

## Details
When configured to use an SSL bundle, Spring Boot's Elasticsearch auto-configuration does not perform hostname verification when connecting to the Elasticsearch server.

Affected: Spring Boot 4.0.0–4.0.5; upgrade to 4.0.6 or later per vendor advisory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40970
- https://github.com/spring-projects/spring-boot
- https://github.com/spring-projects/spring-boot/releases/tag/v4.0.6
- https://spring.io/security/cve-2026-40970
