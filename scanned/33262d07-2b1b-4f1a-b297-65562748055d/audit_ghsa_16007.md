# [M] Langchain Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hc5w-c9f8-9cc4
CVE: CVE-2024-7774
CWE: CWE-22, CWE-29
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-hc5w-c9f8-9cc4
Type: github-advisory

## Affected
- npm: `langchain` — affected >=0 <0.2.19

## Details
A path traversal vulnerability exists in the `getFullPath` method of langchain-ai/langchainjs version 0.2.5. This vulnerability allows attackers to save files anywhere in the filesystem, overwrite existing text files, read `.txt` files, and delete files. The vulnerability is exploited through the `setFileContent`, `getParsedFile`, and `mdelete` methods, which do not properly sanitize user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7774
- https://github.com/langchain-ai/langchainjs/commit/a0fad77d6b569e5872bd4a9d33be0c0785e538a9
- https://github.com/langchain-ai/langchainjs
- https://github.com/pypa/advisory-database/tree/main/vulns/langchain/PYSEC-2024-111.yaml
- https://huntr.com/bounties/8fe40685-b714-4191-af7a-3de5e5628cee
