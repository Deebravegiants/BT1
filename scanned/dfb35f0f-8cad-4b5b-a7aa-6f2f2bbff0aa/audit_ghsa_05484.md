# [M] Gitea does not properly validate repository ownership when deleting Git LFS locks

## Summary
Severity: Medium
Advisory: GHSA-393c-qgvj-3xph
CVE: CVE-2026-20897
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-393c-qgvj-3xph
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.25.4

## Details
Gitea does not properly validate repository ownership when deleting Git LFS locks. A user with write access to one repository may be able to delete LFS locks belonging to other repositories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-20897
- https://github.com/go-gitea/gitea/pull/36344
- https://github.com/go-gitea/gitea/pull/36349
- https://github.com/go-gitea/gitea/commit/da036f3f35ca830b22cf4480912ed261303b798f
- https://blog.gitea.com/release-of-1.25.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.4
