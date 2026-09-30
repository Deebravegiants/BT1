# [M] LlamaIndex vulnerable to data loss through hash collisions in its DocugamiReader class 

## Summary
Severity: Medium
Advisory: GHSA-5hq9-5r78-2gjh
CVE: CVE-2025-6211
CWE: CWE-440
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-5hq9-5r78-2gjh
Type: github-advisory

## Affected
- PyPI: `llama-index` — affected >=0 <0.12.41
- PyPI: `llama-index-readers-docugami` — affected >=0 <0.3.1

## Details
A vulnerability in the DocugamiReader class of the run-llama/llama_index repository, up to but excluding version 0.12.41, involves the use of MD5 hashing to generate IDs for document chunks. This approach leads to hash collisions when structurally distinct chunks contain identical text, resulting in one chunk overwriting another. This can cause loss of semantically or legally important document content, breakage of parent-child chunk hierarchies, and inaccurate or hallucinated responses in AI outputs. The issue is resolved in version 0.3.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6211
- https://github.com/run-llama/llama_index/commit/29b2e07e64ed7d302b1cc058185560b28eaa1352
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/1a48a011-a3c5-4979-9ffc-9652280bc389
