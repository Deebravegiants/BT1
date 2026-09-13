# [M] SQL Injection in langchain-ai/langchain

## Summary
Severity: Medium
Advisory: CVE-2024-8309
Aliases: GHSA-45pg-36p6-83v9, PYSEC-2024-115, PYSEC-2026-1507
CVSS: 4.9 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-8309
Type: osv

## Details
A vulnerability in the GraphCypherQAChain class of langchain-ai/langchain version 0.2.5 allows for SQL injection through prompt injection. This vulnerability can lead to unauthorized data manipulation, data exfiltration, denial of service (DoS) by deleting all data, breaches in multi-tenant security environments, and data integrity issues. Attackers can create, update, or delete nodes and relationships without proper authorization, extract sensitive data, disrupt services, access data across different tenants, and compromise the integrity of the database.

## References
- https://huntr.com/bounties/8f4ad910-7fdc-4089-8f0a-b5df5f32e7c5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8309.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8309
- https://github.com/langchain-ai/langchain/commit/c2a3021bb0c5f54649d380b42a0684ca5778c255
