# [H] SQLBot: Unauthorized Access Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-42463
Aliases: GHSA-pq2r-fj48-xfpp
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-42463
Type: osv

## Details
SQLBot is an intelligent Text-to-SQL system based on large language models and RAG. Prior to 1.8.0, SQLBot contains a Cross-Workspace IDOR (Insecure Direct Object Reference) and Authorization Bypass vulnerability in the /api/v1/datasource/exportDsSchema and /api/v1/datasource/uploadDsSchema endpoints. An attacker can access and modify database schemas and data sources belonging to other tenants/workspaces. This vulnerability is fixed in 1.8.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42463.json
- https://github.com/dataease/SQLBot/security/advisories/GHSA-pq2r-fj48-xfpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-42463
