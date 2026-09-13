# [C] CVE-2024-27444

## Summary
Severity: Critical
Advisory: CVE-2024-27444
Aliases: GHSA-v8vj-cv27-hjv8, PYSEC-2026-375
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2024-27444
Type: osv

## Details
langchain_experimental (aka LangChain Experimental) in LangChain before 0.1.8 allows an attacker to bypass the CVE-2023-44467 fix and execute arbitrary code via the __import__, __subclasses__, __builtins__, __globals__, __getattribute__, __bases__, __mro__, or __base__ attribute in Python code. These are not prohibited by pal_chain/base.py.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27444.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27444
- https://github.com/langchain-ai/langchain/commit/de9a6cdf163ed00adaf2e559203ed0a9ca2f1de7
