# [C] AnythingLLM has SQL Injection in Built-in SQL Agent Plugin via Unsanitized table_name Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-32628
Aliases: GHSA-jwjx-mw2p-5wc7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32628
Type: osv

## Details
AnythingLLM is an application that turns pieces of content into context that any LLM can use as references during chatting. In 1.11.1 and earlier, a SQL injection vulnerability in the built-in SQL Agent plugin allows any user who can invoke the agent to execute arbitrary SQL commands on connected databases. The getTableSchemaSql() method in all three database connectors (MySQL, PostgreSQL, MSSQL) constructs SQL queries using direct string concatenation of the table_name parameter without sanitization or parameterization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32628.json
- https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-jwjx-mw2p-5wc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-32628
- https://github.com/Mintplex-Labs/anything-llm/commit/334ce052f063b53a4275518cbed3bab357695d7e
