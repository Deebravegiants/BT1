# [H] Mattermost allows remote actor to create/update/delete posts in arbitrary channels

## Summary
Severity: High
Advisory: GHSA-vg67-chm7-8m3j
CVE: CVE-2024-41144
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-vg67-chm7-8m3j
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.7
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.7.0 <9.7.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20240619142046-8181a9ddffc0
- Go: `github.com/mattermost/mattermost` — affected >=0 <5.3.2-0.20240619142046-8181a9ddffc0

## Details
Mattermost versions 9.9.x <= 9.9.0, 9.5.x <= 9.5.6, 9.7.x <= 9.7.5, 9.8.x <= 9.8.1 fail to properly validate synced posts, when shared channels are enabled,  which allows a malicious remote to create/update/delete arbitrary posts in arbitrary channels

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41144
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-3023
