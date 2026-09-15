# [M] Guest user can discover active public channels

## Summary
Severity: Medium
Advisory: CVE-2025-41443
Aliases: GHSA-7cr3-38jm-6p45, GO-2025-4031
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-41443
Type: osv

## Details
Mattermost versions 10.5.x <= 10.5.12, 10.11.x <= 10.11.2 fail to properly validate guest user permissions when accessing channel information which allows guest users to discover active public channels and their metadata via the `/api/v4/teams/{team_id}/channels/ids` endpoint

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/41xxx/CVE-2025-41443.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-41443
