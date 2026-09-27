# [H] Spring AI vector store metadata filtering to handle special characters in Elasticsearch, OpenSearch, and GemFire Vector Stores

## Summary
Severity: High
Advisory: GHSA-cmwh-w62w-r2mf
CVE: CVE-2026-47835
CWE: CWE-943
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-cmwh-w62w-r2mf
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-opensearch-store` — affected >=1.0.0 <1.0.9
- Maven: `org.springframework.ai:spring-ai-opensearch-store` — affected >=1.1.0 <1.1.8
- Maven: `org.springframework.ai:spring-ai-elasticsearch-store` — affected >=1.0.0 <1.0.9
- Maven: `org.springframework.ai:spring-ai-elasticsearch-store` — affected >=1.1.0 <1.1.8
- Maven: `org.springframework.ai:spring-ai-gemfire-store` — affected >=1.0.0 <1.0.9
- Maven: `org.springframework.ai:spring-ai-gemfire-store` — affected >=1.1.0 <1.1.8

## Details
In Spring AI Vector Stores, special characters could be used to force the execution of arbitrary queries in Elasticsearch, OpenSearch, and GemFire VectorDB. Affected components: spring-ai-elasticsearch-store, spring-ai-opensearch-store, spring-ai-gemfire-store.

Affected versions:
Spring AI 1.0.0 through 1.0.x (fix 1.0.9).
Spring AI 1.1.0 through 1.1.x (fix 1.1.8).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-47835
- https://github.com/spring-projects/spring-ai/commit/2b20cfc8f478444f942d4be7a867d254441ff991
- https://github.com/spring-projects/spring-ai/commit/9787991aa1ed92c511131ddf4e142bd94051e6e7
- https://github.com/spring-projects/spring-ai
- https://github.com/spring-projects/spring-ai/releases/tag/v1.0.9
- https://github.com/spring-projects/spring-ai/releases/tag/v1.1.8
- https://spring.io/security/cve-2026-47835
