# [M] Mattermost fails to properly validate team membership when processing channel mentions

## Summary
Severity: Medium
Advisory: GHSA-57cc-2pf4-mhmx
CVE: CVE-2025-14350
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-16
Source: https://github.com/advisories/GHSA-57cc-2pf4-mhmx
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20251209134645-761e56bb11cc
- Go: `github.com/mattermost/mattermost-server` — affected >=11.1.0
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20251209134645-761e56bb11cc

## Details
Mattermost versions 11.1.x <= 11.1.2, 10.11.x <= 10.11.9, 11.2.x <= 11.2.1 fail to properly validate team membership when processing channel mentions which allows authenticated users to determine the existence of teams and their URL names via posting channel shortlinks and observing the channel_mentions property in the API response. Mattermost Advisory ID: MMSA-2025-00563

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14350
- https://github.com/mattermost/mattermost/commit/761e56bb11ccb751ddbe4bab5898ccc2b384fd82
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
