# [M] Spring Data MongoDB Has Regex Parameter Binding Injection in @Query Repository Methods

## Summary
Severity: Medium
Advisory: GHSA-hc43-m36c-8v33
CVE: CVE-2026-41696
CWE: CWE-943
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-hc43-m36c-8v33
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-mongodb` — affected >=5.0.0 <5.0.6
- Maven: `org.springframework.data:spring-data-mongodb` — affected >=4.5.0 <4.5.12
- Maven: `org.springframework.data:spring-data-mongodb` — affected >=4.4.0
- Maven: `org.springframework.data:spring-data-mongodb` — affected >=4.0.0
- Maven: `org.springframework.data:spring-data-mongodb` — affected >=0

## Details
Spring Data MongoDB repository query methods annotated with @Query that use regex parameter binding perform insufficient validation of the bound parameter. An attacker can supply a crafted string to break out of the intended regular expression quoting.

Affected versions:
Spring Data MongoDB 5.0.0 through 5.0.5; 4.5.0 through 4.5.11; 4.4.0 through 4.4.14; 4.3.0 through 4.3.16; 4.2.0 through 4.2.15; 4.1.0 through 4.1.14; 4.0.0 through 4.0.15; 3.4.0 through 3.4.19.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41696
- https://github.com/spring-projects/spring-data-mongodb/issues/5205
- https://github.com/spring-projects/spring-data-mongodb/commit/24d5afc0c7df223150e06fce3f64c226bcc88ca2
- https://github.com/spring-projects/spring-data-mongodb/commit/7d2ea784d262bf4bf4ea8402505f491c8ab66fcc
- https://github.com/spring-projects/spring-data-mongodb
- https://spring.io/security/cve-2026-41696
