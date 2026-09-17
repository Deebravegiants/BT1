# [M] Gitea does not properly validate project ownership in organization project operations

## Summary
Severity: Medium
Advisory: GHSA-rw22-5hhq-pfpf
CVE: CVE-2026-20750
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-rw22-5hhq-pfpf
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.25.4

## Details
Gitea does not properly validate project ownership in organization project operations. A user with project write access in one organization may be able to modify projects belonging to a different organization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-20750
- https://github.com/go-gitea/gitea/pull/36318
- https://github.com/go-gitea/gitea/pull/36373
- https://github.com/go-gitea/gitea/commit/7b5de594cd92e30b9c3d40ffda119acad794cc64
- https://blog.gitea.com/release-of-1.25.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.4
