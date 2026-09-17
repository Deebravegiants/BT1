# [H] OpenViking contains a Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-rpqr-j937-6qr9
CVE: CVE-2026-28518
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-rpqr-j937-6qr9
Type: github-advisory

## Affected
- PyPI: `openviking` — affected >=0

## Details
OpenViking versions 0.2.1 and prior, fixed in commit 46b3e76, contain a path traversal vulnerability in the .ovpack import handling that allows attackers to write files outside the intended import directory. Attackers can craft malicious ZIP archives with traversal sequences, absolute paths, or drive prefixes in member names to overwrite or create arbitrary files with the importing process privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28518
- https://github.com/volcengine/OpenViking/issues/342
- https://github.com/volcengine/OpenViking/commit/46b3e76e28b9b3eee73693720c9ec48820228b72
- https://github.com/volcengine/OpenViking
- https://www.vulncheck.com/advisories/openviking-ovpack-import-zip-slip-path-traversal
