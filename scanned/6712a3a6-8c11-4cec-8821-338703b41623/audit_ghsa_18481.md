# [H] LlamaIndex is vulnerable to Path Traversal attack through its ObsidianReader class

## Summary
Severity: High
Advisory: GHSA-fmrf-6jv9-qjc7
CVE: CVE-2025-3046
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-07
Source: https://github.com/advisories/GHSA-fmrf-6jv9-qjc7
Type: github-advisory

## Affected
- PyPI: `llama-index-readers-obsidian` — affected >=0 <0.5.1

## Details
A vulnerability in the `ObsidianReader` class in LlamaIndex Readers Integration: Obsidian before version 0.5.1 from the run-llama/llama_index repository (versions 0.12.23 to 0.12.28) allows for arbitrary file read through symbolic links. The `ObsidianReader` fails to resolve symlinks to their real paths and does not validate whether the resolved paths lie within the intended directory. This flaw enables attackers to place symlinks pointing to files outside the vault directory, which are then processed as valid Markdown files, potentially exposing sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3046
- https://github.com/run-llama/llama_index/pull/18320
- https://github.com/run-llama/llama_index/commit/0008041e8dde8e519621388e5d6f558bde6ef42e
- https://github.com/run-llama/llama_index/commit/266eb3b3a61f158112726d75a5f5f0b90e34ded0
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/90a1f1b2-bb82-4d66-9fc1-856ed5f904da
