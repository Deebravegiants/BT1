# [H] Gitea git grep searches allow server resource exhaustion

## Summary
Severity: High
Advisory: GHSA-h9c5-x7g8-4q7f
CVE: CVE-2026-26307
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-h9c5-x7g8-4q7f
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.5

## Details
Gitea versions before 1.25.5 do not enforce a timeout on git grep searches, allowing expensive searches to consume server resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26307
- https://github.com/go-gitea/gitea/pull/36809
- https://github.com/go-gitea/gitea/pull/36835
- https://github.com/go-gitea/gitea/commit/5d87bb3d4566e71b791a8114bfc9e25c037ab5fe
- https://github.com/go-gitea/gitea/commit/f7e3569fab57d3525280670dffcc30c84c87b115
- https://blog.gitea.com/release-of-1.25.5
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5
