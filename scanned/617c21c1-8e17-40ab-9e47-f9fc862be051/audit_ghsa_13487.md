# [C] langchain_experimental vulnerable to arbitrary code execution via PALChain in the python exec method

## Summary
Severity: Critical
Advisory: GHSA-gjjr-63x4-v8cq
CVE: CVE-2023-44467
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-09
Source: https://github.com/advisories/GHSA-gjjr-63x4-v8cq
Type: github-advisory

## Affected
- PyPI: `langchain-experimental` — affected >=0

## Details
langchain_experimental (aka LangChain Experimental) in LangChain before 0.0.306 allows an attacker to bypass the CVE-2023-36258 fix and execute arbitrary code via __import__ in Python code, which is not prohibited by pal_chain/base.py.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-44467
- https://github.com/langchain-ai/langchain/pull/11233
- https://github.com/langchain-ai/langchain/commit/4c97a10bd0d9385cfee234a63b5bd826a295e483
- https://github.com/langchain-ai/langchain
- https://github.com/pypa/advisory-database/tree/main/vulns/langchain-experimental/PYSEC-2023-194.yaml
- https://pypi.org/project/langchain-experimental/0.0.14
