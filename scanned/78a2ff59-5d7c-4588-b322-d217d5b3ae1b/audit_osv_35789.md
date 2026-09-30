# [M] BigQuery Dataset Allowlist Bypass via Metadata Dry-Run in MCP Toolbox

## Summary
Severity: Medium
Advisory: CVE-2026-14538
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/E:U)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-14538
Type: osv

## Details
An improper authorization and security-boundary bypass vulnerability in the bigquery-execute-sql tool component of Google mcp-toolbox versions 0.16.1 through 1.4.0 allows an authenticated attacker to bypass allowedDatasets validation checks. The toolbox relies on the BigQuery dry-run API to enforce dataset restrictions, but due to a fail-open logic flaw, it bypasses validation when the API returns an empty array for specialized constructs. This allows the attacker to extract structural DDL schemas for explicitly excluded datasets via INFORMATION_SCHEMA, and access downstream federated row data via EXTERNAL_QUERY connections.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14538.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14538
- https://github.com/googleapis/mcp-toolbox/pull/3452
