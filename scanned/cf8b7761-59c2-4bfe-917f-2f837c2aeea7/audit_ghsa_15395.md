# [M] Mattermost allows guest user with read access to upload files to a channel

## Summary
Severity: Medium
Advisory: GHSA-2jhx-w3vc-w59g
CVE: CVE-2024-43780
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-2jhx-w3vc-w59g
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.10.0 <9.10.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.3

## Details
Mattermost versions 9.9.x <= 9.9.1, 9.5.x <= 9.5.7, 9.10.0, 9.8.x <= 9.8.2 fail to enforce permissions which allows a guest user with read access to upload files to a channel.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43780
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
