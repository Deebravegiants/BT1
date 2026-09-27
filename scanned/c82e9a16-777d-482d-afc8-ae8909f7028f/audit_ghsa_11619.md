# [H] Spring AI Redis Store has TAG Field Query Injection Through Improper Neutralization of Special Characters

## Summary
Severity: High
Advisory: GHSA-44f4-gvwj-6qg3
CVE: CVE-2026-22744
CWE: CWE-74, CWE-943
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-44f4-gvwj-6qg3
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-redis-store` — affected >=1.0.0-M5 <1.0.5
- Maven: `org.springframework.ai:spring-ai-redis-store` — affected >=1.1.0-M1 <1.1.4

## Details
In RedisFilterExpressionConverter of spring-ai-redis-store, when a user-controlled string is passed as a filter value for a TAG field, stringValue() inserts the value directly into the @field:{VALUE} RediSearch TAG block without escaping characters. This issue affects Spring AI: from 1.0.0 before 1.0.5, from 1.1.0 before 1.1.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22744
- https://github.com/spring-projects/spring-ai/commit/707e990c9152aabb9c9226053725efa2ada72223
- https://github.com/spring-projects/spring-ai
- https://github.com/spring-projects/spring-ai/releases/tag/v1.0.5
- https://github.com/spring-projects/spring-ai/releases/tag/v1.1.4
- https://spring.io/security/cve-2026-22744
