# [M] Mattermost allows a remote actor to permanently delete local data by abusing dangerous error handling

## Summary
Severity: Medium
Advisory: GHSA-762m-4cx6-6mf4
CVE: CVE-2024-39832
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-762m-4cx6-6mf4
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.7
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.7.0 <9.7.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.1

## Details
Mattermost versions 9.9.x <= 9.9.0, 9.5.x <= 9.5.6, 9.7.x <= 9.7.5, 9.8.x <= 9.8.1 fail to properly safeguard an error handling which allows a malicious remote to permanently delete local data by abusing dangerous error handling, when share channels were enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39832
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-3020
