# [M] memos lacks file name validation or verification

## Summary
Severity: Medium
Advisory: GHSA-qgjp-5g5x-vhq2
CVE: CVE-2025-65799
CWE: CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-qgjp-5g5x-vhq2
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.25.3

## Details
A lack of file name validation or verification in the Attachment service of usememos memos v0.25.2 allows attackers to execute a path traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65799
- https://github.com/usememos/memos/pull/5218
- https://github.com/usememos/memos/commit/5f57f48673e2054f404b2c5b497a8eaa3690591d
- https://github.com/advisories/GHSA-qgjp-5g5x-vhq2
- https://github.com/usememos/memos
- https://herolab.usd.de/security-advisories/usd-2025-0056
- http://memos.com
- http://usememos.com
