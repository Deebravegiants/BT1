# [M] Mattermost Fails to Verify User's Permissions When Accessing Groups

## Summary
Severity: Medium
Advisory: GHSA-h356-3mfw-x368
CVE: CVE-2025-2527
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-05-15
Source: https://github.com/advisories/GHSA-h356-3mfw-x368
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0 <10.5.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.12
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250411064244-844447fbd57c

## Details
Mattermost versions 10.5.x <= 10.5.2, 9.11.x <= 9.11.11 failed to properly verify a user's permissions when accessing groups, which allows an attacker to view group information via an API request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2527
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
