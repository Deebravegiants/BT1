# [H] Spring Data Commons: Heap exhaustion from unbounded property-lookup cache retaining crafted string keys

## Summary
Severity: High
Advisory: GHSA-9fw2-h3hf-293r
CVE: CVE-2026-41716
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-9fw2-h3hf-293r
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-commons` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.data:spring-data-commons` — affected >=3.5.0 <3.5.12
- Maven: `org.springframework.data:spring-data-commons` — affected >=3.4.0
- Maven: `org.springframework.data:spring-data-commons` — affected >=3.3.0
- Maven: `org.springframework.data:spring-data-commons` — affected >=0

## Details
Spring Data's internal property-lookup cache accepts and permanently retains attacker-supplied strings as cache keys, allowing heap exhaustion through repeated requests.

Affected versions:
Spring Data Commons 2.7.0 through 2.7.19; 3.3.0 through 3.3.16; 3.4.0 through 3.4.14; 3.5.0 through 3.5.11; 4.0.0 through 4.0.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41716
- https://github.com/spring-projects/spring-data-commons
- https://github.com/spring-projects/spring-data-commons/releases/tag/3.5.12
- https://github.com/spring-projects/spring-data-commons/releases/tag/4.0.6
- https://spring.io/security/cve-2026-41716
