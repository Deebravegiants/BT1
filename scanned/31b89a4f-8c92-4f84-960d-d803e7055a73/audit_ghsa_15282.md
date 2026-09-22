# [M] Mattermost failed to properly validate synced reactions

## Summary
Severity: Medium
Advisory: GHSA-jq3g-xqpx-37x3
CVE: CVE-2024-29977
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-jq3g-xqpx-37x3
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.7
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.1

## Details
Mattermost versions 9.9.x <= 9.9.0, 9.5.x <= 9.5.6 fail to properly validate synced reactions, when shared channels are enabled, which allows a malicious remote to create arbitrary reactions on arbitrary posts

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29977
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-3030
