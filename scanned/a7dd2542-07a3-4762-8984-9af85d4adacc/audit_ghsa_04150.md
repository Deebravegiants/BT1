# [M] Spring Data KeyValue: Remote code execution via SpEL Injection in Sort-based repository queries

## Summary
Severity: Medium
Advisory: GHSA-xg2j-3hj6-pc24
CVE: CVE-2026-41719
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-xg2j-3hj6-pc24
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-keyvalue` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.data:spring-data-keyvalue` — affected >=3.5.0 <3.5.12
- Maven: `org.springframework.data:spring-data-keyvalue` — affected >=3.4.0
- Maven: `org.springframework.data:spring-data-keyvalue` — affected >=3.0.0
- Maven: `org.springframework.data:spring-data-keyvalue` — affected >=0

## Details
A SpEL Injection vulnerability exists in the Spring Data KeyValue if unsanitized user input is passed as Sort into a repository query method that delegates evaluation to the SpelPropertyComparator.

Affected versions:
Spring Data KeyValue / Spring Data Redis 4.0.0 through 4.0.5; 3.5.0 through 3.5.11; 3.4.0 through 3.4.14; 3.3.0 through 3.3.16; 3.2.0 through 3.2.15; 3.1.0 through 3.1.14; 3.0.0 through 3.0.15; 2.7.0 through 2.7.19.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41719
- https://github.com/spring-projects/spring-data-keyvalue
- https://github.com/spring-projects/spring-data-keyvalue/releases/tag/3.5.12
- https://github.com/spring-projects/spring-data-keyvalue/releases/tag/4.0.6
- https://spring.io/security/cve-2026-41719
