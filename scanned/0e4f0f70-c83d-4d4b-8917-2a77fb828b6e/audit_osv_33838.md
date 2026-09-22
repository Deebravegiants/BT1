# [M] CVE-2025-51458

## Summary
Severity: Medium
Advisory: CVE-2025-51458
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-51458
Type: osv

## Details
SQL Injection in editor_sql_run and query_ex in eosphoros-ai DB-GPT 0.7.0 allows remote attackers to execute arbitrary SQL statements via crafted input passed to the /v1/editor/sql/run or /v1/editor/chart/run endpoints, interacting with api_editor_v1.editor_sql_run, editor_chart_run, and datasource.rdbms.base.query_ex.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51458.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51458
- https://github.com/eosphoros-ai/DB-GPT/pull/2650
- https://www.gecko.security/blog/cve-2025-51458
