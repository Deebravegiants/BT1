# [C] Gitea repository creation accepts insufficiently validated fields

## Summary
Severity: Critical
Advisory: GHSA-922f-hfwp-p56f
CVE: CVE-2026-22547
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-922f-hfwp-p56f
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.25.5

## Details
Gitea versions before 1.25.5 lack validation constraints for repository creation fields, including length-limited template fields and trust model or object format values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22547
- https://github.com/go-gitea/gitea/pull/36671
- https://github.com/go-gitea/gitea/pull/36757
- https://github.com/go-gitea/gitea/commit/569c49debe06f30a2bbb50b3812e705c556b8adf
- https://github.com/go-gitea/gitea/commit/b3bc79262d106f4259f82a26609e4738b618152b
- https://blog.gitea.com/release-of-1.25.5
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5
