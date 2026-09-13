# [H] Gitea forwarded-proto validation allows canonical URL spoofing

## Summary
Severity: High
Advisory: GHSA-v8f2-2ghq-9whv
CVE: CVE-2026-27779
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-v8f2-2ghq-9whv
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.5

## Details
Gitea versions before 1.25.5 accept malformed or injected forwarded-proto values when detecting public URLs, allowing spoofed canonical URL generation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27779
- https://github.com/go-gitea/gitea/pull/36810
- https://github.com/go-gitea/gitea/pull/36836
- https://github.com/go-gitea/gitea/commit/723ce3579f96e75fd12514283023a051a1432b1b
- https://github.com/go-gitea/gitea/commit/e2517e0fa93177ef6947245eaeab543c95ef18ff
- https://blog.gitea.com/release-of-1.25.5
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5
