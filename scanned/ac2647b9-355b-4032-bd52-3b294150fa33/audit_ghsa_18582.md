# [M] LlamaIndex vulnerable to DoS attack through uncontrolled recursive JSON parsing

## Summary
Severity: Medium
Advisory: GHSA-3wxx-q3gv-pvvv
CVE: CVE-2025-5472
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-07-07
Source: https://github.com/advisories/GHSA-3wxx-q3gv-pvvv
Type: github-advisory

## Affected
- PyPI: `llama-index-core` — affected >=0 <0.12.38

## Details
The JSONReader in run-llama/llama_index versions 0.12.28 is vulnerable to a stack overflow due to uncontrolled recursive JSON parsing. This vulnerability allows attackers to trigger a Denial of Service (DoS) by submitting deeply nested JSON structures, leading to a RecursionError and crashing applications. The root cause is the unsafe recursive traversal design and lack of depth validation, which makes the JSONReader susceptible to stack overflow when processing deeply nested JSON. This impacts the availability of services, making them unreliable and disrupting workflows. The issue is resolved in version 0.12.38.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5472
- https://github.com/run-llama/llama_index/commit/c032843a02ce38fd8f284b2aa5a37fd1c17ae635
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/df187bda-7911-4823-a19a-e15b2c66b0d4
