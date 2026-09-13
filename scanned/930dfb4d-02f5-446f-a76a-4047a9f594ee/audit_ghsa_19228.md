# [H] LlamaIndex Vulnerable to Denial of Service (DoS)

## Summary
Severity: High
Advisory: GHSA-7c85-87cp-mr6g
CVE: CVE-2025-1752
CWE: CWE-400, CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-10
Source: https://github.com/advisories/GHSA-7c85-87cp-mr6g
Type: github-advisory

## Affected
- PyPI: `llama-index` — affected >=0.12.15 <0.12.21

## Details
A Denial of Service (DoS) vulnerability has been identified in the KnowledgeBaseWebReader class of the run-llama/llama_index project, affecting version ~ latest(v0.12.15). The vulnerability arises due to inappropriate secure coding measures, specifically the lack of proper implementation of the max_depth parameter in the get_article_urls function. This allows an attacker to exhaust Python's recursion limit through repeated function calls, leading to resource consumption and ultimately crashing the Python process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1752
- https://github.com/run-llama/llama_index/commit/3c65db2947271de3bd1927dc66a044da385de4da
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/cd7b9082-7d75-42e4-84f5-dbee23cbc467
