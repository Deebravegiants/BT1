# [C] Mattermost failed to properly validate that the channel that comes from the sync message is a shared channel

## Summary
Severity: Critical
Advisory: GHSA-cmc8-222c-vqp9
CVE: CVE-2024-39274
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-cmc8-222c-vqp9
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.7
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.7.0 <9.7.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.1

## Details
Mattermost versions 9.9.x <= 9.9.0, 9.5.x <= 9.5.6, 9.7.x <= 9.7.5 and 9.8.x <= 9.8.1 fail to properly validate that the channel that comes from the sync message is a shared channel, when shared channels are enabled, which allows a malicious remote to add users to arbitrary teams and channels

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39274
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-3028
