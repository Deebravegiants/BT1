# [H] Spring for GraphQL: Cross-Site WebSocket Hijacking

## Summary
Severity: High
Advisory: GHSA-m39w-hqxx-3r48
CVE: CVE-2026-41700
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-m39w-hqxx-3r48
Type: github-advisory

## Affected
- Maven: `org.springframework.graphql:spring-graphql` — affected >=2.0.0 <2.0.4
- Maven: `org.springframework.graphql:spring-graphql` — affected >=1.4.0 <1.4.6
- Maven: `org.springframework.graphql:spring-graphql` — affected >=1.3.0
- Maven: `org.springframework.graphql:spring-graphql` — affected >=1.0.0

## Details
Spring for GraphQL applications that have enabled the WebSocket transport are vulnerable to Cross-Site WebSocket Hijacking. An attacker can trick an authenticated user into visiting a malicious page, allowing the attacker to execute arbitrary GraphQL operations with the victim's credentials.

Affected versions:
Spring for GraphQL 2.0.0 through 2.0.3; 1.4.0 through 1.4.5; 1.3.0 through 1.3.8; 1.0.0 through 1.0.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41700
- https://github.com/spring-projects/spring-graphql/commit/3ebad2713f52e04e6dc892b5adb79a29e14f4a1a
- https://github.com/spring-projects/spring-graphql
- https://spring.io/security/cve-2026-41700
