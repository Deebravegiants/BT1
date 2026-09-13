# [C] SQL Injection to RCE in run-llama/llama_index

## Summary
Severity: Critical
Advisory: CVE-2024-12909
Aliases: GHSA-x48g-hm9c-ww42, PYSEC-2026-398
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12909
Type: osv

## Details
A vulnerability in the FinanceChatLlamaPack of the run-llama/llama_index repository, versions up to v0.12.3, allows for SQL injection in the `run_sql_query` function of the `database_agent`. This vulnerability can be exploited by an attacker to inject arbitrary SQL queries, leading to remote code execution (RCE) through the use of PostgreSQL's large object functionality. The issue is fixed in version 0.3.0.

## References
- https://huntr.com/bounties/44e8177f-200a-4ba3-a12c-8bc21e313a3f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12909.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12909
- https://github.com/run-llama/llama_index/commit/5d03c175476452db9b8abcdb7d5767dd7b310a75
