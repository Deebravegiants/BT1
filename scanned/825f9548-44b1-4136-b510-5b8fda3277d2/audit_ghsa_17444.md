# [M] Gitea mishandles access to a private resource upon receiving an API token with scope limited to public resources

## Summary
Severity: Medium
Advisory: GHSA-xfq3-qj7j-4565
CVE: CVE-2025-68941
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-xfq3-qj7j-4565
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.22.3

## Details
Gitea before 1.22.3 mishandles access to a private resource upon receiving an API token with scope limited to public resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68941
- https://github.com/go-gitea/gitea/pull/32218
- https://blog.gitea.com/release-of-1.22.3
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.22.3
