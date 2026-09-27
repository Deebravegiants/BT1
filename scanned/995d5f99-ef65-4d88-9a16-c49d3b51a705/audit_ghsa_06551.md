# [H] Gitea organization permission APIs expose hidden membership and private organization data

## Summary
Severity: High
Advisory: GHSA-37w2-86g3-h4qh
CVE: CVE-2026-25712
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-37w2-86g3-h4qh
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.5

## Details
Gitea versions before 1.25.5 have insufficient visibility checks in organization permission APIs for hidden members and private organizations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25712
- https://github.com/go-gitea/gitea/pull/36798
- https://github.com/go-gitea/gitea/pull/36841
- https://github.com/go-gitea/gitea/commit/57b5ed3f252753797e790c060c42fbbe8219b9c1
- https://github.com/go-gitea/gitea/commit/96515c0f200d37228dc84a599c6177297a230c94
- https://blog.gitea.com/release-of-1.25.5
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5
