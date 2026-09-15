# [M] Spring Data Relational: Attackers can supply wildcard characters to perform boolean-based blind data inference

## Summary
Severity: Medium
Advisory: GHSA-8r2h-xh92-gq57
CVE: CVE-2026-41697
CWE: CWE-943
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-8r2h-xh92-gq57
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-relational` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.data:spring-data-relational` — affected >=3.5.0 <3.5.12
- Maven: `org.springframework.data:spring-data-relational` — affected >=3.4.0
- Maven: `org.springframework.data:spring-data-relational` — affected >=3.0.0
- Maven: `org.springframework.data:spring-data-relational` — affected >=0

## Details
Spring Data Relational does not properly escape binding values of externally-controlled input when using StringMatcher (STARTING, ENDING, or CONTAINING) in Query By Example (QBE). An attacker can supply wildcard characters to perform boolean-based blind data inference.

Affected versions:
Spring Data Relational/JDBC/R2DBC 4.0.0 through 4.0.5; 3.5.0 through 3.5.11; 3.4.0 through 3.4.14; 3.3.0 through 3.3.16; 3.2.0 through 3.2.15; 3.1.0 through 3.1.14; 3.0.0 through 3.0.15; 2.4.0 through 2.4.19.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41697
- https://github.com/spring-projects/spring-data-relational
- https://github.com/spring-projects/spring-data-relational/releases/tag/3.5.12
- https://github.com/spring-projects/spring-data-relational/releases/tag/4.0.6
- https://spring.io/security/cve-2026-41697
