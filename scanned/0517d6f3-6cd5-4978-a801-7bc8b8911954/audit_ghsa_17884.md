# [H] LlamaIndex affected by a Denial of Service (DOS) in JSONReader

## Summary
Severity: High
Advisory: GHSA-7753-xrfw-ch36
CVE: CVE-2025-5302
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2025-08-26
Source: https://github.com/advisories/GHSA-7753-xrfw-ch36
Type: github-advisory

## Affected
- PyPI: `llama-index-core` — affected >=0 <0.12.38

## Details
A denial of service vulnerability exists in the JSONReader component of the run-llama/llama_index repository, specifically in version v0.12.37. The vulnerability is caused by uncontrolled recursion when parsing deeply nested JSON files, which can lead to Python hitting its maximum recursion depth limit. This results in high resource consumption and potential crashes of the Python process. The issue is resolved in version 0.12.38.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5302
- https://github.com/run-llama/llama_index/commit/c032843a02ce38fd8f284b2aa5a37fd1c17ae635
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/70041b81-de9e-4046-8c0e-6ccd557048a6
