# [M] BBOT: Path traversal (Zip-Slip) in unarchive module - incomplete fix for CVE-2025-10284

## Summary
Severity: Medium
Advisory: GHSA-3vgw-585j-4m45
CVE: CVE-2026-12565
CWE: CWE-22, CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-3vgw-585j-4m45
Type: github-advisory

## Affected
- PyPI: `bbot` — affected >=2.3.1 <2.8.5

## Details
The `unarchive` internal module's archive extraction commands perform no code-level validation on extracted file paths, relying entirely on the behavior of external tools (e.g. GNU tar) which varies by platform. While CVE-2025-10284 addressed git-specific RCE vectors, the underlying archive extraction path traversal was never fixed. On systems with GNU tar < 1.34 (Ubuntu 20.04, Debian Buster, CentOS 7, many Docker base images), a malicious archive can write files outside the intended extraction directory.

## References
- https://github.com/blacklanternsecurity/bbot/security/advisories/GHSA-3vgw-585j-4m45
- https://nvd.nist.gov/vuln/detail/CVE-2026-12565
- https://github.com/blacklanternsecurity/bbot/commit/4fb38fd6e
- https://github.com/blacklanternsecurity/bbot
