# [M] Gitea sometimes mishandles propagation of token scope for access control within one of its own package registries

## Summary
Severity: Medium
Advisory: GHSA-f85h-c7m6-cfpm
CVE: CVE-2025-68944
CWE: CWE-441
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-f85h-c7m6-cfpm
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.22.2

## Details
Gitea before 1.22.2 sometimes mishandles the propagation of token scope for access control within one of its own package registries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68944
- https://github.com/go-gitea/gitea/pull/31967
- https://blog.gitea.com/release-of-1.22.2
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.22.2
