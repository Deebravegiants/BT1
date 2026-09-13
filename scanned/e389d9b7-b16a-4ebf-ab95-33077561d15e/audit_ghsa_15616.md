# [H] GraphQL Java does not properly consider ExecutableNormalizedFields (ENFs) as part of preventing denial of service

## Summary
Severity: High
Advisory: GHSA-h9mq-f6q5-6c8m
CVE: CVE-2024-40094
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-30
Source: https://github.com/advisories/GHSA-h9mq-f6q5-6c8m
Type: github-advisory

## Affected
- Maven: `com.graphql-java:graphql-java` — affected >=0 <19.11
- Maven: `com.graphql-java:graphql-java` — affected >=20.0 <20.9
- Maven: `com.graphql-java:graphql-java` — affected >=21.0 <21.5

## Details
GraphQL Java (aka graphql-java) before 21.5 does not properly consider ExecutableNormalizedFields (ENFs) as part of preventing denial of service via introspection queries. 20.9 and 19.11 are also fixed versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-40094
- https://github.com/graphql-java/graphql-java/pull/3539
- https://github.com/graphql-java/graphql-java/commit/16c159111507ef04d7e1839b2c23281d90c42b2b
- https://github.com/graphql-java/graphql-java/commit/469caf6ee600ab6709ad5e8a06f371fe2ef3b8dd
- https://github.com/graphql-java/graphql-java/commit/97743bc1b5caa2b0bd894dc8e128b47e4d771e4a
- https://github.com/graphql-java/graphql-java/commit/fc6f304e66cab18b6d06a80c7009524938939a03
- https://github.com/graphql-java/graphql-java/discussions/3641
- https://github.com/graphql-java/graphql-java/releases/tag/v19.11
- https://github.com/graphql-java/graphql-java/releases/tag/v20.9
- https://github.com/graphql-java/graphql-java/releases/tag/v21.5
