# [M] Gitea inadvertently discloses users' login times by allowing (for example) the lastlogintime explore/users sort order

## Summary
Severity: Medium
Advisory: GHSA-jhx5-4vr4-f327
CVE: CVE-2025-68943
CWE: CWE-497
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-jhx5-4vr4-f327
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.21.8

## Details
Gitea before 1.21.8 inadvertently discloses users' login times by allowing (for example) the lastlogintime explore/users sort order.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68943
- https://github.com/go-gitea/gitea/pull/29430
- https://blog.gitea.com/release-of-1.21.8-and-1.21.9-and-1.21.10
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.21.8
