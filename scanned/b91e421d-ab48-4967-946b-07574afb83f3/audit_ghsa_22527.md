# [M] Mattermost Server's Session ID and Session Token are potentially compromised

## Summary
Severity: Medium
Advisory: GHSA-43m6-wvc8-2m7j
CVE: CVE-2016-11072
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-43m6-wvc8-2m7j
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.0.2

## Details
An issue was discovered in Mattermost Server before 3.0.2. The purposes of a session ID and a Session Token were mishandled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-11072
- https://github.com/mattermost/mattermost/commit/ac509b114df1c1b4b841eded74fb797805e0162d
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
