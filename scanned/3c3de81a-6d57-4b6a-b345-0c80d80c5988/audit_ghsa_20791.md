# [H] graphql-java vulnerable to Denial of Service via GraphQL query that consumes CPU resources

## Summary
Severity: High
Advisory: GHSA-v62j-cxhh-fq22
CVE: CVE-2022-37734
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-13
Source: https://github.com/advisories/GHSA-v62j-cxhh-fq22
Type: github-advisory

## Affected
- Maven: `com.graphql-java:graphql-java` — affected >=0 <17.4
- Maven: `com.graphql-java:graphql-java` — affected >=18.0 <18.3

## Details
graphql-java before 19.0, 18.3, and 17.4 is vulnerable to Denial of Service. An attacker send a malicious GraphQL query that consumes CPU resources. The fixed versions are 19.0, 18.3, and 17.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37734
- https://github.com/graphql-java/graphql-java/issues/2888
- https://github.com/graphql-java/graphql-java/pull/2892
- https://github.com/graphql-java/graphql-java
- https://github.com/graphql-java/graphql-java/discussions/2958
- https://github.com/graphql-java/graphql-java/releases
- https://security.snyk.io/vuln/SNYK-JAVA-COMGRAPHQLJAVA-3021519
