# [M] Soft Serve does not sanitize ANSI escape sequences in user input

## Summary
Severity: Medium
Advisory: GHSA-fv2r-r8mp-pg48
CVE: CVE-2025-64494
CWE: CWE-150
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-06
Source: https://github.com/advisories/GHSA-fv2r-r8mp-pg48
Type: github-advisory

## Affected
- Go: `github.com/charmbracelet/soft-serve` — affected >=0 <0.11.0

## Details
### Impact
In several places where the user can insert data (e.g. names), ANSI escape sequences are not being removed, which can then be used, for example, to show fake alerts.

In the same token, git messages, when printed, are also not being sanitized.

Places in which this was found:

1. Repository Description (pkg/backend/repo.go - SetDescription)
2. Repository Project Name (pkg/backend/repo.go - SetProjectName)
3. Git Commit Author Names (pkg/ssh/cmd/commit.go:69)
4. Git Commit Messages (pkg/ssh/cmd/commit.go:71)
5. Access Token Names (pkg/ssh/cmd/token.go:107)
6. Webhook URLs (pkg/ssh/cmd/webhooks.go:72)

### Patches
v0.11.0

### Workarounds
No.

### References
n/a

## References
- https://github.com/charmbracelet/soft-serve/security/advisories/GHSA-fv2r-r8mp-pg48
- https://nvd.nist.gov/vuln/detail/CVE-2025-64494
- https://github.com/charmbracelet/soft-serve/commit/d9639320b8d0ccd76fe6836a042c042b0ebde549
- https://github.com/charmbracelet/soft-serve
