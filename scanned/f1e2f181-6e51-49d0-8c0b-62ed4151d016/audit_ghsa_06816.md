# [M] Gitea release asset dumps permit path traversal through crafted names

## Summary
Severity: Medium
Advisory: GHSA-7jvx-g65v-r899
CVE: CVE-2026-28705
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-7jvx-g65v-r899
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.5

## Details
Gitea versions before 1.25.5 use release tag names and asset names as filesystem path components when dumping release assets, allowing specially crafted names to affect dump output paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28705
- https://github.com/go-gitea/gitea/pull/36799
- https://github.com/go-gitea/gitea/pull/36839
- https://github.com/go-gitea/gitea/commit/833304ac15bce17d0f03c4852af5f60c186f6a70
- https://github.com/go-gitea/gitea/commit/f7ac5076711af3a260f3f98b2c1f8c19b32f6d09
- https://blog.gitea.com/release-of-1.25.5
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5
