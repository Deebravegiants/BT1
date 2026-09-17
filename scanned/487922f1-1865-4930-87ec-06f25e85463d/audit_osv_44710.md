# [M] Postgres MCP Pro 0.3.0 Restricted-Mode Bypass via FROM-Clause Function

## Summary
Severity: Medium
Advisory: CVE-2026-85620
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85620
Type: osv

## Details
Postgres MCP Pro 0.3.0 contains a restricted-mode bypass vulnerability where function-name validation is not applied to RangeFunction nodes in FROM clauses. Attackers can execute file-reading functions like pg_read_file through FROM-clause syntax to read arbitrary files despite restricted-mode protections.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85620.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85620
- https://www.vulncheck.com/advisories/postgres-mcp-pro-0.3.0-restricted-mode-bypass-via-from-clause-function
- https://github.com/crystaldba/postgres-mcp/issues/178
- https://github.com/crystaldba/postgres-mcp
- https://github.com/crystaldba/postgres-mcp/blob/v0.3.0/src/postgres_mcp/sql/safe_sql.py
