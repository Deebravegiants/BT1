# [H] langchain_experimental Code Execution via Python REPL access

## Summary
Severity: High
Advisory: GHSA-wmvm-9vqv-5qpp
CVE: CVE-2024-38459
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-16
Source: https://github.com/advisories/GHSA-wmvm-9vqv-5qpp
Type: github-advisory

## Affected
- PyPI: `langchain-experimental` — affected >=0 <0.0.61

## Details
langchain_experimental (aka LangChain Experimental) before 0.0.61 for LangChain provides Python REPL access without an opt-in step. NOTE; this issue exists because of an incomplete fix for CVE-2024-27444.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38459
- https://github.com/langchain-ai/langchain/pull/22860
- https://github.com/langchain-ai/langchain/commit/ce0b0f22a175139df8f41cdcfb4d2af411112009
- https://github.com/langchain-ai/langchain
- https://github.com/langchain-ai/langchain/compare/langchain-experimental==0.0.60...langchain-experimental==0.0.61
- https://github.com/pypa/advisory-database/tree/main/vulns/langchain-experimental/PYSEC-2024-53.yaml
