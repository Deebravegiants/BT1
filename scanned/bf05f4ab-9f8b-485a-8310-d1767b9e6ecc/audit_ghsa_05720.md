# [M] Gitea does not properly validate repository ownership when linking attachments to releases

## Summary
Severity: Medium
Advisory: GHSA-4xx9-vc8v-87hv
CVE: CVE-2026-20912
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-4xx9-vc8v-87hv
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.25.4

## Details
Gitea does not properly validate repository ownership when linking attachments to releases. An attachment uploaded to a private repository could potentially be linked to a release in a different public repository, making it accessible to unauthorized users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-20912
- https://github.com/go-gitea/gitea/pull/36320
- https://github.com/go-gitea/gitea/pull/36355
- https://github.com/go-gitea/gitea/commit/fbea2c68e8df11cfa94e8ead913b79946780ed30
- https://blog.gitea.com/release-of-1.25.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.25.4
