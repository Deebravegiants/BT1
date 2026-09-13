# [H] Spring for GraphQL: Annotation Detection Vulnerability

## Summary
Severity: High
Advisory: GHSA-phxq-526m-79px
CVE: CVE-2026-41856
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-phxq-526m-79px
Type: github-advisory

## Affected
- Maven: `org.springframework.graphql:spring-graphql` — affected >=2.0.0 <2.0.4
- Maven: `org.springframework.graphql:spring-graphql` — affected >=1.4.0 <1.4.6
- Maven: `org.springframework.graphql:spring-graphql` — affected >=1.3.0
- Maven: `org.springframework.graphql:spring-graphql` — affected >=1.0.0

## Details
The Spring GraphQL annotation detection mechanism for @Controller data fetchers may not correctly resolve annotations on methods within type hierarchies. This can be an issue if such annotations are used for authorization decisions. When all conditions are met, security annotations can be ignored at runtime.

Affected versions:
Spring for GraphQL 2.0.0 through 2.0.3; 1.4.0 through 1.4.5; 1.3.0 through 1.3.8; 1.0.0 through 1.0.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41856
- https://github.com/spring-projects/spring-graphql/commit/63a89ed1379be646822dca9779b15dbf2ce45839
- https://github.com/spring-projects/spring-graphql
- https://spring.io/security/cve-2026-41856
