# [M] llama-index-core vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: Medium
Advisory: GHSA-488g-hw5f-x29p
CVE: CVE-2025-6208
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-488g-hw5f-x29p
Type: github-advisory

## Affected
- PyPI: `llama-index-core` — affected >=0 <0.12.41

## Details
The `SimpleDirectoryReader` component in `llama_index.core` version 0.12.23 suffers from uncontrolled memory consumption due to a resource management flaw. The vulnerability arises because the user-specified file limit (`num_files_limit`) is applied after all files in a directory are loaded into memory. This can lead to memory exhaustion and degraded performance, particularly in environments with limited resources. The issue is resolved in version 0.12.41.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6208
- https://github.com/run-llama/llama_index/commit/53614e2f7913c0e86b58add9470b3c900b6c60b2
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/7d722bb6-6567-4608-8b23-f95048d7605a
