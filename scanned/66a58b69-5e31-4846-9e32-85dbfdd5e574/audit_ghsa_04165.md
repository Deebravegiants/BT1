# [H] Spring Data MongoDB is vulnerable to SpEL (Spring Expression Language) expression injection

## Summary
Severity: High
Advisory: GHSA-5whc-4q84-fj73
CVE: CVE-2026-41717
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-5whc-4q84-fj73
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-mongodb` — affected >=5.0.0 <5.0.6
- Maven: `org.springframework.data:spring-data-mongodb` — affected >=4.5.0 <4.5.12
- Maven: `org.springframework.data:spring-data-mongodb` — affected >=4.4.0
- Maven: `org.springframework.data:spring-data-mongodb` — affected >=4.0.0
- Maven: `org.springframework.data:spring-data-mongodb` — affected >=0

## Details
Spring Data MongoDB contains a SpEL (Spring Expression Language) expression injection vulnerability. The issue occurs during parameter binding when a user-defined repository query method is annotated with @Query and utilizes a capture-all placeholder.

Affected versions:
Spring Data MongoDB 5.0.0 through 5.0.5; 4.5.0 through 4.5.11; 4.4.0 through 4.4.14; 4.3.0 through 4.3.16; 4.2.0 through 4.2.15; 4.1.0 through 4.1.14; 4.0.0 through 4.0.15; 3.4.0 through 3.4.19.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41717
- https://github.com/spring-projects/spring-data-mongodb
- https://github.com/spring-projects/spring-data-mongodb/releases/tag/4.5.12
- https://github.com/spring-projects/spring-data-mongodb/releases/tag/5.0.6
- https://spring.io/security/cve-2026-41717
