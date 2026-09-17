# [M] Gitea's /api/v1/user endpoint has different responses for failed authentication depending on whether a username exists

## Summary
Severity: Medium
Advisory: GHSA-pc73-rj2c-wvf9
CVE: CVE-2025-69413
CWE: CWE-204
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-01
Source: https://github.com/advisories/GHSA-pc73-rj2c-wvf9
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.2

## Details
In Gitea before 1.25.2, /api/v1/user has different responses for failed authentication depending on whether a username exists.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69413
- https://github.com/go-gitea/gitea/issues/35984
- https://github.com/go-gitea/gitea/pull/36002
- https://blog.gitea.com/release-of-1.25.2
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.2
