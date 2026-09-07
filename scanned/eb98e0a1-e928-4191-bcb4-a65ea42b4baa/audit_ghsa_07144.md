# [C] Gitea OAuth2 PKCE S256 verifier bypass

## Summary
Severity: Critical
Advisory: GHSA-m5ch-ppfx-xv3v
CVE: CVE-2026-26247
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-m5ch-ppfx-xv3v
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.5

## Details
Gitea versions before 1.25.5 do not persist the OAuth2 PKCE S256 challenge method correctly during authorization, allowing token exchange without the expected verifier check.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26247
- https://github.com/go-gitea/gitea/pull/36462
- https://github.com/go-gitea/gitea/pull/36477
- https://github.com/go-gitea/gitea/commit/750649c1ef092c95f95b206b9d5fa17471a0b1f5
- https://github.com/go-gitea/gitea/commit/bf8d11bb212ba2a76596d8a90e74e7d664571324
- https://blog.gitea.com/release-of-1.25.5
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5
