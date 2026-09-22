# [H] Spring AI's MilvusVectorStore#doDelete(List) implementation is vulnerable to filter-expression injection via unsanitized document IDs

## Summary
Severity: High
Advisory: GHSA-v632-2m87-7469
CVE: CVE-2026-41705
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-05-09
Source: https://github.com/advisories/GHSA-v632-2m87-7469
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-milvus-store` — affected >=1.0.0 <1.0.7
- Maven: `org.springframework.ai:spring-ai-milvus-store` — affected >=1.1.0 <1.1.6
- Maven: `org.springframework.ai:spring-ai-typesense-store` — affected >=1.0.0 <1.0.7
- Maven: `org.springframework.ai:spring-ai-typesense-store` — affected >=1.1.0 <1.1.6

## Details
Spring AI's MilvusVectorStore#doDelete(List) implementation is vulnerable to filter-expression injection via unsanitized document IDs.
Spring AI 1.0.x: affected from 1.0.0 through latest 1.0.x; upgrade to 1.0.7 or greater. Spring AI 1.1.x: affected from 1.1.0 through latest 1.1.x; upgrade to 1.1.6 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41705
- https://github.com/spring-projects/spring-ai/pull/6011
- https://github.com/spring-projects/spring-ai
- https://spring.io/security/cve-2026-41705
