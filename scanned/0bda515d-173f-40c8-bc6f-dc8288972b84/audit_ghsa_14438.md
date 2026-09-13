# [H] GraphQL Java vulnerable to stack consumption

## Summary
Severity: High
Advisory: GHSA-p4qx-6w5p-4rj2
CVE: CVE-2023-28867
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-p4qx-6w5p-4rj2
Type: github-advisory

## Affected
- Maven: `com.graphql-java:graphql-java` — affected >=0 <0.0.0-2023-03-20T01-49-44-80e3135
- Maven: `com.graphql-java:graphql-java` — affected >=1.2 <17.5
- Maven: `com.graphql-java:graphql-java` — affected >=18.0 <18.4
- Maven: `com.graphql-java:graphql-java` — affected >=19.0 <19.4
- Maven: `com.graphql-java:graphql-java` — affected >=20.0 <20.1

## Details
In GraphQL Java (aka graphql-java) before 20.1, an attacker can send a crafted GraphQL query that causes stack consumption. The fixed versions are 20.1, 19.4, 18.4, 17.5, and 0.0.0-2023-03-20T01-49-44-80e3135.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28867
- https://github.com/graphql-java/graphql-java/pull/3112
- https://github.com/graphql-java/graphql-java
- https://github.com/graphql-java/graphql-java/releases/tag/v17.5
- https://github.com/graphql-java/graphql-java/releases/tag/v18.4
- https://github.com/graphql-java/graphql-java/releases/tag/v19.4
- https://github.com/graphql-java/graphql-java/releases/tag/v20.1
