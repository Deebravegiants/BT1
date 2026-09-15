# [C] InvokeAI Arbitrary File Deletion vulnerability

## Summary
Severity: Critical
Advisory: GHSA-227r-w5j2-6243
CVE: CVE-2024-11042
CWE: CWE-20, CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-227r-w5j2-6243
Type: github-advisory

## Affected
- PyPI: `InvokeAI` — affected >=0 <5.3.0rc1

## Details
In invoke-ai/invokeai version v5.0.2, the web API `POST /api/v1/images/delete` is vulnerable to Arbitrary File Deletion. This vulnerability allows unauthorized attackers to delete arbitrary files on the server, potentially including critical or sensitive system files such as SSH keys, SQLite databases, and configuration files. This can impact the integrity and availability of applications relying on these files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11042
- https://github.com/invoke-ai/invokeai/commit/5440c037674882b2ab7acd59087e9bb04b49657a
- https://github.com/invoke-ai/InvokeAI
- https://huntr.com/bounties/635535a7-c804-4789-ac3a-48d951263987
