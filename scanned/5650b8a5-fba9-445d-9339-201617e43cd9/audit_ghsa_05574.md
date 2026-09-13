# [M] Gitea does not properly validate ownership when toggling OpenID URI visibility

## Summary
Severity: Medium
Advisory: GHSA-qqgv-v353-cv8p
CVE: CVE-2026-20904
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-qqgv-v353-cv8p
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.25.4

## Details
Gitea does not properly validate ownership when toggling OpenID URI visibility. An authenticated user may be able to change the visibility settings of other users' OpenID identities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-20904
- https://github.com/go-gitea/gitea/pull/36346
- https://github.com/go-gitea/gitea/pull/36361
- https://github.com/go-gitea/gitea/commit/ed5720af2ac94d74f822721c05b42b6148ff9c22
- https://blog.gitea.com/release-of-1.25.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.4
