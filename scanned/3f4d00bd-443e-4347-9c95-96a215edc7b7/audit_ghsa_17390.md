# [H] Gitea allows attackers to add attachments with forbidden file extensions

## Summary
Severity: High
Advisory: GHSA-263q-5cv3-xq9g
CVE: CVE-2025-68939
CWE: CWE-424
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-263q-5cv3-xq9g
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0

## Details
Gitea before 1.23.0 allows attackers to add attachments with forbidden file extensions by editing an attachment name via an attachment API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68939
- https://github.com/go-gitea/gitea/pull/32151
- https://blog.gitea.com/release-of-1.23.0
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.23.0
