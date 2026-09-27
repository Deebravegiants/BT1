# [M] Prompt Injection in langchain-ai/langchainjs Leading to SQL Injection

## Summary
Severity: Medium
Advisory: CVE-2024-7042
Aliases: GHSA-6m59-8fmv-m5f9
CVSS: 4.9 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-7042
Type: osv

## Details
A vulnerability in the GraphCypherQAChain class of langchain-ai/langchainjs versions 0.2.5 and all versions with this class allows for prompt injection, leading to SQL injection. This vulnerability permits unauthorized data manipulation, data exfiltration, denial of service (DoS) by deleting all data, breaches in multi-tenant security environments, and data integrity issues. Attackers can create, update, or delete nodes and relationships without proper authorization, extract sensitive data, disrupt services, access data across different tenants, and compromise the integrity of the database.

## References
- https://huntr.com/bounties/b612defb-1104-4fff-9fef-001ab07c7b2d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7042.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7042
- https://github.com/langchain-ai/langchainjs/commit/615b9d9ab30a2d23a2f95fb8d7acfdf4b41ad7a6
