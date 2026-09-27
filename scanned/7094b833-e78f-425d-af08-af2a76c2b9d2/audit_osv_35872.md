# [H] SQL Injection and Security Boundary Bypass in googleapis/mcp-toolbox

## Summary
Severity: High
Advisory: CVE-2026-15829
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-15829
Type: osv

## Details
A SQL injection (CWE-89) and security boundary bypass (CWE-863) vulnerability exists in the prebuilt BigQuery forecasting tool (bigquery-forecast) of googleapis/mcp-toolbox.

The tool accepts client-controlled parameters (data_col, timestamp_col, and id_cols) as plain strings and interpolates them unescaped via fmt.Sprintf directly into a generated AI.FORECAST table-valued SELECT statement. While MCP Toolbox utilizes an allowedDatasets mechanism to restrict queries, this defense only validates the history_data parameter; the final assembled query is executed without re-validation.

An attacker can break out of the string literal fields (such as timestamp_col) to inject a valid multi-statement or cross-dataset query block. This allows an unauthorized user to bypass the operator-configured allowedDatasets boundary and read arbitrary BigQuery tables.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15829.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15829
- https://github.com/googleapis/mcp-toolbox/pull/3324
