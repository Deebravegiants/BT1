# [M] Mattermost notified all users in the channel when using WebSockets to respond individually

## Summary
Severity: Medium
Advisory: GHSA-q7rx-w656-fwmv
CVE: CVE-2023-48732
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-02
Source: https://github.com/advisories/GHSA-q7rx-w656-fwmv
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.7
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <8.1.7

## Details
Mattermost fails to scope the WebSocket response around notified users to a each user separately resulting in the WebSocket broadcasting the information about who was notified about a post to everyone else in the channel.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48732
- https://github.com/mattermost/mattermost/commit/851515be222160bee0a495c0d411056b19ed4111
- https://github.com/advisories/GHSA-q7rx-w656-fwmv
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
