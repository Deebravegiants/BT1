# [H] LangChain Server Side Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-655w-fm8m-m478
CVE: CVE-2023-46229
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-655w-fm8m-m478
Type: github-advisory

## Affected
- PyPI: `langchain` — affected >=0 <0.0.317

## Details
LangChain before 0.0.317 allows SSRF via `document_loaders/recursive_url_loader.py` because crawling can proceed from an external server to an internal server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46229
- https://github.com/langchain-ai/langchain/pull/11925
- https://github.com/langchain-ai/langchain/commit/9ecb7240a480720ec9d739b3877a52f76098a2b8
- https://github.com/langchain-ai/langchain
- https://github.com/pypa/advisory-database/tree/main/vulns/langchain/PYSEC-2023-205.yaml
