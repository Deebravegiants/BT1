# [M] Mattermost Improper Access Control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jj46-9cgh-qmfx
CVE: CVE-2023-47865
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-jj46-9cgh-qmfx
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.4
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.13

## Details
Mattermost fails to check if hardened mode is enabled when overriding the username and/or the icon when posting a post. If settings allowed integrations to override the username and profile picture when posting, a member could also override the username and icon when making a post even if the Hardened Mode setting was enabled

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47865
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
