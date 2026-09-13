# [H] Spring AI has a Cypher Injection vulnerability in Neo4jVectorFilterExpressionConverter

## Summary
Severity: High
Advisory: GHSA-7cj7-rcw6-p68v
CVE: CVE-2026-22743
CWE: CWE-89, CWE-943
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-7cj7-rcw6-p68v
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-neo4j-store` — affected >=1.0.0-M5 <1.0.5
- Maven: `org.springframework.ai:spring-ai-neo4j-store` — affected >=1.1.0-M1 <1.1.4

## Details
Spring AI's spring-ai-neo4j-store contains a Cypher injection vulnerability in Neo4jVectorFilterExpressionConverter. When a user-controlled string is passed as a filter expression key in Neo4jVectorFilterExpressionConverter of spring-ai-neo4j-store, doKey() embeds the key into a backtick-delimited Cypher property accessor (node.`metadata.`) after stripping only double quotes, without escaping embedded backticks. This issue affects Spring AI: from 1.0.0 before 1.0.5, from 1.1.0 before 1.1.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22743
- https://github.com/spring-projects/spring-ai/commit/3a46c7dd00e4adc17a132b9438149bde94da244f
- https://github.com/spring-projects/spring-ai
- https://github.com/spring-projects/spring-ai/releases/tag/v1.0.5
- https://github.com/spring-projects/spring-ai/releases/tag/v1.1.4
- https://spring.io/security/cve-2026-22743
