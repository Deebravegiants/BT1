# [M] Mattermost Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4ghx-8jw8-p76q
CVE: CVE-2023-47168
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-4ghx-8jw8-p76q
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.1.0 <9.1.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.0.0 <9.0.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.4
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.13

## Details
Mattermost fails to properly check a redirect URL parameter allowing for an open redirect was possible when the user clicked "Back to Mattermost" after providing a invalid custom url scheme in /oauth/{service}/mobile_login?redirect_to=

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47168
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
