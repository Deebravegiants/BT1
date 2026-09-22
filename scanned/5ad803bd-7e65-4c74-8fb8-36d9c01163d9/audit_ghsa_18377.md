# [M] LlamaIndex vulnerability in ArxivReader class can cause MD5 hash collisions

## Summary
Severity: Medium
Advisory: GHSA-p7j4-jwjf-5x9w
CVE: CVE-2025-3044
CWE: CWE-440
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-07-07
Source: https://github.com/advisories/GHSA-p7j4-jwjf-5x9w
Type: github-advisory

## Affected
- PyPI: `llama-index-readers-papers` — affected >=0 <0.3.1

## Details
A vulnerability in the ArxivReader class of the run-llama/llama_index repository allows for MD5 hash collisions when generating filenames for downloaded papers. This can lead to data loss as papers with identical titles but different contents may overwrite each other, preventing some papers from being processed for AI model training. The issue is resolved in llama-index-readers-papers version 0.3.1 (in llama-index 0.12.28).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3044
- https://github.com/run-llama/llama_index/commit/0008041e8dde8e519621388e5d6f558bde6ef42e
- https://github.com/run-llama/llama_index/commit/f69e1c0e7579228fec4cfaf716e4f951e131de77
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/80182c3a-876f-422f-8bac-38267e0345d6
