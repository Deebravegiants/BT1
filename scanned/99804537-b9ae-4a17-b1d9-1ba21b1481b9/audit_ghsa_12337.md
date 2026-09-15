# [M] Mattermost Exposure of Sensitive Information to an Unauthorized Actor vulnerability

## Summary
Severity: Medium
Advisory: GHSA-63cv-4pc2-4fcf
CVE: CVE-2023-6459
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-06
Source: https://github.com/advisories/GHSA-63cv-4pc2-4fcf
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.14
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.5

## Details
Mattermost is grouping calls in the /metrics endpoint by id and reports that id in the response. Since this id is the channelID, the public /metrics endpoint is revealing channelIDs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6459
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
