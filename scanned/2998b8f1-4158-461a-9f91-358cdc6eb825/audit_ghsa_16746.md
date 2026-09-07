# [H] RunGptLLM class in LlamaIndex has a command injection

## Summary
Severity: High
Advisory: GHSA-pw38-xv9x-h8ch
CVE: CVE-2024-4181
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-16
Source: https://github.com/advisories/GHSA-pw38-xv9x-h8ch
Type: github-advisory

## Affected
- PyPI: `llama-index` — affected >=0 <0.10.13
- PyPI: `llama-index-llms-rungpt` — affected >=0 <0.1.3

## Details
A command injection vulnerability exists in the RunGptLLM class of the llama_index library, version 0.9.47, used by the RunGpt framework from JinaAI to connect to Language Learning Models (LLMs). The vulnerability arises from the improper use of the eval function, allowing a malicious or compromised LLM hosting provider to execute arbitrary commands on the client's machine. This issue was fixed in version 0.10.13. The exploitation of this vulnerability could lead to a hosting provider gaining full control over client machines.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4181
- https://github.com/run-llama/llama_index/commit/d73715eaf0642705583e7897c78b9c8dd2d3a7ba
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/1a204520-598a-434e-b13d-0d34f2a5ddc1
