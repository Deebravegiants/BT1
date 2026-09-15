# [M] Gitea does not properly verify authorization when canceling scheduled auto-merges via the web interface

## Summary
Severity: Medium
Advisory: GHSA-9cgq-wp42-4rpq
CVE: CVE-2026-20888
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-9cgq-wp42-4rpq
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.25.4

## Details
Gitea does not properly verify authorization when canceling scheduled auto-merges via the web interface. A user with read access to pull requests may be able to cancel auto-merges scheduled by other users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-20888
- https://github.com/go-gitea/gitea/pull/36341
- https://github.com/go-gitea/gitea/pull/36356
- https://blog.gitea.com/release-of-1.25.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.4
