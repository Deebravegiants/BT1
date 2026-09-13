# [H] Gitea draft releases and attachments are exposed without write permission

## Summary
Severity: High
Advisory: GHSA-x92v-f5gc-r34v
CVE: CVE-2026-27660
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-x92v-f5gc-r34v
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.5

## Details
Gitea versions before 1.25.5 allow draft release data or attachments to be accessed without the required write permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27660
- https://github.com/go-gitea/gitea/pull/36659
- https://github.com/go-gitea/gitea/pull/36715
- https://github.com/go-gitea/gitea/commit/1eced4a7c099459af42412bb32a83241650c0f8f
- https://github.com/go-gitea/gitea/commit/e7fca90a780e4d35eb1fa67b1f377ebd54e74611
- https://blog.gitea.com/release-of-1.25.5
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5
