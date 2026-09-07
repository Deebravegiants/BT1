# [C] LangChain Experimental Eval Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-p2qj-r53j-h3xj
CVE: CVE-2024-46946
CWE: CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-19
Source: https://github.com/advisories/GHSA-p2qj-r53j-h3xj
Type: github-advisory

## Affected
- PyPI: `langchain-experimental` — affected >=0.1.17

## Details
langchain_experimental (aka LangChain Experimental) 0.1.17 through 0.3.0 for LangChain allows attackers to execute arbitrary code through sympy.sympify (which uses eval) in LLMSymbolicMathChain. LLMSymbolicMathChain was introduced in fcccde406dd9e9b05fc9babcbeb9ff527b0ec0c6 (2023-10-05).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46946
- https://docs.sympy.org/latest/modules/codegen.html
- https://gist.github.com/12end/68c0c58d2564ef4141bccd4651480820#file-cve-2024-46946-txt
- https://github.com/langchain-ai/langchain
- https://github.com/langchain-ai/langchain/releases/tag/langchain-experimental%3D%3D0.3.0
