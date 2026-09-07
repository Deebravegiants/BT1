# [C] DB-GPT Absolute Path Traversal in knowledge/{space_name}/document/upload

## Summary
Severity: Critical
Advisory: GHSA-j9g7-mqhh-9hxf
CVE: CVE-2024-10833
CWE: CWE-22, CWE-36
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-j9g7-mqhh-9hxf
Type: github-advisory

## Affected
- PyPI: `dbgpt` — affected >=0 <0.6.2

## Details
eosphoros-ai/db-gpt version 0.6.0 is vulnerable to an arbitrary file write through the knowledge API. The endpoint for uploading files as 'knowledge' is susceptible to absolute path traversal, allowing attackers to write files to arbitrary locations on the target server. This vulnerability arises because the 'doc_file.filename' parameter is user-controllable, enabling the construction of absolute paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10833
- https://github.com/eosphoros-ai/DB-GPT/commit/780ce803e325b87f4ddfbe5824451e379aeee56c
- https://github.com/eosphoros-ai/DB-GPT
- https://huntr.com/bounties/dc58e981-e325-4c11-b4e1-1095890fd15a
