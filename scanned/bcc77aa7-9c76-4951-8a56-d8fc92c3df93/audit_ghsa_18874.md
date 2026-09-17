# [H] llama-index has Insecure Temporary File

## Summary
Severity: High
Advisory: GHSA-rg9h-vx28-xxp5
CVE: CVE-2025-7707
CWE: CWE-377
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-rg9h-vx28-xxp5
Type: github-advisory

## Affected
- PyPI: `llama-index` — affected >=0 <0.13.0

## Details
The llama_index library version 0.12.33 sets the NLTK data directory to a subdirectory of the codebase by default, which is world-writable in multi-user environments. This configuration allows local users to overwrite, delete, or corrupt NLTK data files, leading to potential denial of service, data tampering, or privilege escalation. The vulnerability arises from the use of a shared cache directory instead of a user-specific one, making it susceptible to local data tampering and denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-7707
- https://github.com/run-llama/llama_index/commit/98816394d57c7f53f847ed7b60725e69d0e7aae4
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/3fe2c8ab-6727-4aef-a0ef-4d2818e48803
