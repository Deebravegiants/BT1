# [H] Spring AI has SQL Injection in CosmosDBVectorStore.doDelete()

## Summary
Severity: High
Advisory: GHSA-63c8-m9m2-cvr3
CVE: CVE-2026-40978
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-63c8-m9m2-cvr3
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-azure-cosmos-db-store` — affected >=1.0.0 <1.0.6
- Maven: `org.springframework.ai:spring-ai-azure-cosmos-db-store` — affected >=1.1.0 <1.1.5

## Details
SQL injection vulnerability in Spring AI's `CosmosDBVectorStore` allows attackers to execute arbitrary SQL queries via crafted document IDs.

Affected versions:
Spring AI: 1.0.0 - 1.0.5 (fixed in 1.0.6), 1.1.0 - 1.1.4 (fixed in 1.1.5).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40978
- https://github.com/spring-projects/spring-ai
- https://spring.io/security/cve-2026-40978
