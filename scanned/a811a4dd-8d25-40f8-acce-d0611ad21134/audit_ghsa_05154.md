# [H] Spring for GraphQL: Unsafe Deserialization

## Summary
Severity: High
Advisory: GHSA-px92-q6rc-6mwv
CVE: CVE-2026-41699
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-px92-q6rc-6mwv
Type: github-advisory

## Affected
- Maven: `org.springframework.graphql:spring-graphql` — affected >=2.0.0 <2.0.4
- Maven: `org.springframework.graphql:spring-graphql` — affected >=1.4.0 <1.4.6
- Maven: `org.springframework.graphql:spring-graphql` — affected >=1.3.0

## Details
Spring for GraphQL applications are vulnerable to Unsafe Deserialization when processing paginated GraphQL queries. An attacker can craft a malicious GraphQL request that can lead to Remote Code Execution when the application exposes a paginated (Connection) field and the classpath contains specific classes that can be leveraged during deserialization.

Affected versions:
Spring for GraphQL 2.0.0 through 2.0.3; 1.4.0 through 1.4.5; 1.3.0 through 1.3.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41699
- https://github.com/spring-projects/spring-graphql/commit/5579b6eca045126a27405b4cb1ae1f38d7577cb7
- https://github.com/spring-projects/spring-graphql
- https://spring.io/security/cve-2026-41699
