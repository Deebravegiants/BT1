# [C] Gitea OAuth2 authorization codes can be reused after expiry

## Summary
Severity: Critical
Advisory: GHSA-5v69-g2m3-3hq3
CVE: CVE-2026-26232
CWE: CWE-294
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-5v69-g2m3-3hq3
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.5

## Details
Gitea versions before 1.25.5 do not consistently enforce OAuth2 authorization code expiry and single-use behavior during token exchange.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26232
- https://github.com/go-gitea/gitea/pull/36797
- https://github.com/go-gitea/gitea/pull/36851
- https://github.com/go-gitea/gitea/commit/413074b1e1dc5718b4865b9493d8cc97e1e128de
- https://github.com/go-gitea/gitea/commit/f3bdcc58aff60b66eba7bd5e9b23457441733dfe
- https://blog.gitea.com/release-of-1.25.5
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5
