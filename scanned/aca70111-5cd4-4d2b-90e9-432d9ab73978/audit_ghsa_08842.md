# [M] Mattermost doesn't enforce slash command trigger-word uniqueness during command updates

## Summary
Severity: Medium
Advisory: GHSA-wvcv-9xpm-7mqc
CVE: CVE-2026-28732
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-wvcv-9xpm-7mqc
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0 <10.11.14
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0 <11.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260306123948-f5fe8ded6b63
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260306123948-f5fe8ded6b63

## Details
Mattermost versions 11.5.x <= 11.5.1, 10.11.x <= 10.11.13, 11.4.x <= 11.4.3 Fail to enforce slash command trigger-word uniqueness during command updates which allows an authenticated team member with Manage Own Slash Commands permission to hijack and impersonate existing system or custom slash commands via editing their own slash command trigger to an already-registered trigger through the command update API. Mattermost Advisory ID: MMSA-2026-00597

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28732
- https://github.com/mattermost/mattermost/commit/f5fe8ded6b633db7804ae25b42ea12ce635d6ea6
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
