# [C] Improper Access Control in Gitea

## Summary
Severity: Critical
Advisory: GHSA-r7h7-chh4-5rvm
CVE: CVE-2020-28991
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-r7h7-chh4-5rvm
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0.9.99 <1.12.6

## Details
Gitea 0.9.99 through 1.12.x before 1.12.6 does not prevent a git protocol path that specifies a TCP port number and also contains newlines (with URL encoding) in ParseRemoteAddr in modules/auth/repo_form.go.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28991
- https://github.com/go-gitea/gitea/pull/13525
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.12.6
