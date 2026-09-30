# [C] SQL injection in llama-index

## Summary
Severity: Critical
Advisory: GHSA-2jxw-4hm4-6w87
CVE: CVE-2024-23751
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-22
Source: https://github.com/advisories/GHSA-2jxw-4hm4-6w87
Type: github-advisory

## Affected
- PyPI: `llama-index` — affected >=0

## Details
LlamaIndex (aka llama_index) through 0.9.35 allows SQL injection via the Text-to-SQL feature in NLSQLTableQueryEngine, SQLTableRetrieverQueryEngine, NLSQLRetriever, RetrieverQueryEngine, and PGVectorSQLQueryEngine. For example, an attacker might be able to delete this year's student records via "Drop the Students table" within English language input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23751
- https://github.com/run-llama/llama_index/issues/9957
- https://github.com/pypa/advisory-database/tree/main/vulns/llama-index/PYSEC-2024-12.yaml
- https://github.com/run-llama/llama_index
