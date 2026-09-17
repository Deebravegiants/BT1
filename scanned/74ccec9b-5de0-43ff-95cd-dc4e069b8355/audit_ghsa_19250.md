# [M] Mattermost improperly allows team administrators to modify team invites

## Summary
Severity: Medium
Advisory: GHSA-4mmr-2w8p-whcr
CVE: CVE-2025-3913
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-05-29
Source: https://github.com/advisories/GHSA-4mmr-2w8p-whcr
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.7.0-rc1 <10.7.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.6.0-rc1 <10.6.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0-rc1 <10.5.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.0.0-rc1 <9.11.13
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250412152950-02c76784380a

## Details
Mattermost versions 10.7.x <= 10.7.0, 10.6.x <= 10.6.2, 10.5.x <= 10.5.3, 9.11.x <= 9.11.12 fail to properly validate permissions when changing team privacy settings, allowing team administrators without the 'invite user' permission to access and modify team invite IDs via the /api/v4/teams/:teamId/privacy endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3913
- https://github.com/mattermost/mattermost/commit/02c76784380acb6802601bd24c205553b9a5a1be
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
