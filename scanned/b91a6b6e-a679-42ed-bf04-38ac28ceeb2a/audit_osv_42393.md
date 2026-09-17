# [M] Flowise 3.1.4 Missing Authorization on Document Store Mutation Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-67621
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-67621
Type: osv

## Details
Flowise through 3.1.4 contains a missing authorization vulnerability that allows authenticated workspace members to perform unauthorized document store operations by accessing unprotected mutation endpoints. Attackers holding only view-level permissions can send direct HTTP requests to the upsert and refresh document store routes to trigger document ingestion, refresh vector database contents, consume embedding API credits, and modify knowledge bases used by downstream chatflows.

## References
- https://flowiseai.com/sunset
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67621.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67621
- https://www.vulncheck.com/advisories/flowise-missing-authorization-on-document-store-mutation-endpoints
- https://github.com/FlowiseAI/Flowise
- https://github.com/Caycon/cve-advisories/blob/main/2026/Flowise/CVE-2026-67621.md
