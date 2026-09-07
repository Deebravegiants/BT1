# [H] Spring Data REST has Improper Access Control in its JSON Patch Implementation

## Summary
Severity: High
Advisory: GHSA-cv39-x4c6-hhp2
CVE: CVE-2026-41728
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-cv39-x4c6-hhp2
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=5.0.0 <5.0.6
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=4.5.0 <4.5.12
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=4.4.0
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=4.3.0
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=0

## Details
Spring Data REST's JSON Patch (application/json-patch+json) implementation does not apply the write-access filter to intermediate path segments when resolving a multi-segment JSON Pointer.

Affected versions:
Spring Data REST 3.7.0 through 3.7.19; 4.3.0 through 4.3.16; 4.4.0 through 4.4.14; 4.5.0 through 4.5.11; 5.0.0 through 5.0.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41728
- https://github.com/spring-projects/spring-data-rest
- https://github.com/spring-projects/spring-data-rest/releases/tag/4.5.12
- https://github.com/spring-projects/spring-data-rest/releases/tag/5.0.6
- https://spring.io/security/cve-2026-41728
