# [C] Gitea LFS mirror operations bypass migration HTTP transport protections

## Summary
Severity: Critical
Advisory: GHSA-rc56-rj3f-xggf
CVE: CVE-2026-26292
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-rc56-rj3f-xggf
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.5

## Details
Gitea versions before 1.25.5 do not use the migration HTTP transport for LFS push and sync mirror operations, bypassing the configured migration transport protections for those LFS requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26292
- https://github.com/go-gitea/gitea/pull/36665
- https://github.com/go-gitea/gitea/pull/36691
- https://github.com/go-gitea/gitea/commit/996cc12bf7d54ae2326f20b4211fff70eb31e74a
- https://github.com/go-gitea/gitea/commit/bcd253a310115045d3ec5e8168a953fbee34dd28
- https://blog.gitea.com/release-of-1.25.5
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5
