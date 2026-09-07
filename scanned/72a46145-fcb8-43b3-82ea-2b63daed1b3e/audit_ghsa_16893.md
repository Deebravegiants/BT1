# [M] langchain vulnerable to path traversal

## Summary
Severity: Medium
Advisory: GHSA-rgp8-pm28-3759
CVE: CVE-2024-3571
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-16
Source: https://github.com/advisories/GHSA-rgp8-pm28-3759
Type: github-advisory

## Affected
- PyPI: `langchain` — affected >=0 <0.0.353

## Details
langchain-ai/langchain is vulnerable to path traversal due to improper limitation of a pathname to a restricted directory ('Path Traversal') in its LocalFileStore functionality. An attacker can leverage this vulnerability to read or write files anywhere on the filesystem, potentially leading to information disclosure or remote code execution. The issue lies in the handling of file paths in the mset and mget methods, where user-supplied input is not adequately sanitized, allowing directory traversal sequences to reach unintended directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3571
- https://github.com/langchain-ai/langchain/commit/aad3d8bd47d7f5598156ff2bdcc8f736f24a7412
- https://github.com/langchain-ai/langchain
- https://huntr.com/bounties/2df3acdc-ee4f-4257-bbf8-a7de3870a9d8
