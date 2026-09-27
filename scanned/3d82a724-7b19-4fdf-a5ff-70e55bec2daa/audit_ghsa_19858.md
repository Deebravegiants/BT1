# [C]  LlamaIndex Retrievers Integration: DuckDBRetriever SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-339r-cjv9-x78g
CVE: CVE-2024-11958
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-339r-cjv9-x78g
Type: github-advisory

## Affected
- PyPI: `llama-index-retrievers-duckdb-retriever` — affected >=0 <0.4.0

## Details
A SQL injection vulnerability exists in the `duckdb_retriever` component of the run-llama/llama_index repository, specifically in llama-index-retrievers-duckdb-retriever prior to v0.4.0. The vulnerability arises from the construction of SQL queries without using prepared statements, allowing an attacker to inject arbitrary SQL code. This can lead to remote code execution (RCE) by installing the shellfs extension and executing malicious commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11958
- https://github.com/run-llama/llama_index/commit/35bd221e948e40458052d30c6ef2779bc965b6d0
- https://github.com/advisories/GHSA-339r-cjv9-x78g
- https://github.com/pypa/advisory-database/tree/main/vulns/llama-index-retrievers-duckdb-retriever/PYSEC-2026-399.yaml
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/8ddf66e1-f74c-4d53-992b-76bc45cacac1
- https://pypi.org/project/llama-index-retrievers-duckdb-retriever
