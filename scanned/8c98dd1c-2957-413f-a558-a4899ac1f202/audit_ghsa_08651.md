# [M] Casdoor: Arbitrary file write possible through Local File System storage provider

## Summary
Severity: Medium
Advisory: GHSA-rmxx-v9rj-vpvg
CVE: CVE-2026-6815
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-rmxx-v9rj-vpvg
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0

## Details
An arbitrary file write vulnerability exists in Casdoor's Local File System storage provider. Due to insufficient path sanitization, an authenticated attacker with administrative privileges can perform a Path Traversal attack to create or overwrite arbitrary files anywhere on the host filesystem, bypassing the application's intended storage sandbox.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6815
- https://github.com/casdoor/casdoor
- https://kb.cert.org/vuls/id/937808
- https://www.kb.cert.org/vuls/id/937808
