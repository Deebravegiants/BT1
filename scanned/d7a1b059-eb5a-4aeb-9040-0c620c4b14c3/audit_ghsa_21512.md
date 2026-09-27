# [M] Denial of service in Mattermost

## Summary
Severity: Medium
Advisory: GHSA-v42f-hq78-8c5m
CVE: CVE-2022-4045
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-23
Source: https://github.com/advisories/GHSA-v42f-hq78-8c5m
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <7.1.4
- Go: `github.com/mattermost/mattermost-server` — affected >=7.2.0 <7.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=7.3.0 <7.3.1

## Details
A denial-of-service vulnerability in the Mattermost allows an authenticated user to crash the server via multiple requests to one of the API endpoints which could fetch a large amount of data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4045
- https://mattermost.com/security-updates
- https://pkg.go.dev/github.com/mattermost/mattermost-server
