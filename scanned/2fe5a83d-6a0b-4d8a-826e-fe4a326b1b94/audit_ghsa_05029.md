# [M] Spring Data REST Querydsl Integration Exposes Persistent Property Paths, Bypassing Jackson Customizations

## Summary
Severity: Medium
Advisory: GHSA-mwpv-rg79-863c
CVE: CVE-2026-41837
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-mwpv-rg79-863c
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=5.0.0 <5.0.6
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=4.5.0 <4.5.12
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=4.4.0
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=4.3.0
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=0

## Details
Spring Data REST's Querydsl integration accepts arbitrary persistent property paths as request-parameter filter keys and does not consider Jackson customizations before handing them to Querydsl.

Affected versions:
Spring Data REST 3.7.0 through 3.7.19; 4.3.0 through 4.3.16; 4.4.0 through 4.4.14; 4.5.0 through 4.5.11; 5.0.0 through 5.0.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41837
- https://github.com/spring-projects/spring-data-rest
- https://spring.io/security/cve-2026-41837
