# [M] Shiori is vulnerable to authentication bypass via a brute force attack

## Summary
Severity: Medium
Advisory: GHSA-mw8h-g64c-rxv4
CVE: CVE-2025-60538
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-mw8h-g64c-rxv4
Type: github-advisory

## Affected
- Go: `github.com/go-shiori/shiori` — affected >=0

## Details
A lack of rate limiting in the login page of shiori v1.7.4 and below allows attackers to bypass authentication via a brute force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60538
- https://github.com/go-shiori/shiori/issues/1138
- https://github.com/go-shiori/shiori
