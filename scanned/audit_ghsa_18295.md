# [M] Mattermost Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3vcm-c42p-3hhf
CVE: CVE-2025-9076
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-3vcm-c42p-3hhf
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250729073403-517ae758cd02
- Go: `github.com/mattermost/mattermost-server` — affected >=10.10.0 <10.10.2

## Details
Mattermost versions 10.10.x <= 10.10.1 fail to properly sanitize user data during shared channel membership synchronization, which allows malicious or compromised remote clusters to access sensitive user information via unsanitized user objects. This vulnerability affects Mattermost Server instances with shared channels enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9076
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
