# [C] DB-GPT Absolute Path Traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-hhw5-29f6-hf4x
CVE: CVE-2024-10831
CWE: CWE-36
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-hhw5-29f6-hf4x
Type: github-advisory

## Affected
- PyPI: `dbgpt` — affected >=0

## Details
In eosphoros-ai/db-gpt version 0.6.0, the endpoint for uploading files is vulnerable to absolute path traversal. This vulnerability allows an attacker to upload arbitrary files to arbitrary locations on the target server. The issue arises because the `file_key` and `doc_file.filename` parameters are user-controllable, enabling the construction of paths outside the intended directory. This can lead to overwriting essential system files, such as SSH keys, for further exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10831
- https://github.com/eosphoros-ai/DB-GPT
- https://huntr.com/bounties/5c34c39f-66d4-414c-ab6a-f7888a5d882a
