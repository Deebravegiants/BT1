# [M] BBOT: Arbitrary File Write in postman_download Module

## Summary
Severity: Medium
Advisory: GHSA-m54h-vhf9-3w3m
CVE: CVE-2026-12568
CWE: CWE-125, CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-m54h-vhf9-3w3m
Type: github-advisory

## Affected
- PyPI: `bbot` — affected >=2.1.0 <2.8.6

## Details
The `postman_download` module uses the workspace `name` field from the Postman API to construct the local directory path without sanitization. If a malicious workspace has a name containing path traversal characters, pathlib resolves the path outside the intended output directory, allowing an attacker to write arbitrary files to the user's system.

## References
- https://github.com/blacklanternsecurity/bbot/security/advisories/GHSA-m54h-vhf9-3w3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-12568
- https://github.com/blacklanternsecurity/bbot/commit/36bc20818
- https://github.com/blacklanternsecurity/bbot
