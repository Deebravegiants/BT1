# [C] DB-GPT vulnerable to Arbitrary File Upload with Path Traversal

## Summary
Severity: Critical
Advisory: GHSA-3xq5-x4fj-rff7
CVE: CVE-2024-10902
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-3xq5-x4fj-rff7
Type: github-advisory

## Affected
- PyPI: `dbgpt` — affected >=0

## Details
In eosphoros-ai/db-gpt version v0.6.0, the web API `POST /v1/personal/agent/upload` is vulnerable to Arbitrary File Upload with Path Traversal. This vulnerability allows unauthorized attackers to upload arbitrary files to the victim's file system at any location. The impact of this vulnerability includes the potential for remote code execution (RCE) by writing malicious files, such as a malicious `__init__.py` in the Python's `/site-packages/` directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10902
- https://github.com/eosphoros-ai/DB-GPT
- https://huntr.com/bounties/f7fbf76e-aa1c-4106-b007-e9579f4f7d5f
