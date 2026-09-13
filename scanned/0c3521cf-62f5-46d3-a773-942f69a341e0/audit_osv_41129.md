# [M] SigNoz 0.130.1 - SQL Injection in Alert History Endpoints via Rule ID Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-57955
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-57955
Type: osv

## Details
SigNoz through 0.130.1 contains a SQL injection vulnerability that allows authenticated attackers to execute arbitrary ClickHouse queries by injecting URL-encoded quotes into the rule ID path parameter of the alert-history endpoints. Attackers can manipulate the unsanitized rule ID interpolated into ClickHouse queries to read all stored traces, logs, and metrics, or abuse the url() function to perform server-side request forgery.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57955.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57955
- https://www.vulncheck.com/advisories/signoz-sql-injection-in-alert-history-endpoints-via-rule-id-parameter
- https://github.com/SigNoz/signoz/issues/11747
- https://github.com/SigNoz/signoz
