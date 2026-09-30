# [M] BIT-mattermost-2024-42000

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-42000
Aliases: CVE-2024-42000
Ecosystem: Bitnami
Published: 2024-11-15
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-42000
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.11.0 <9.11.2, >=10.0.0

## Details
Mattermost versions 9.10.x <= 9.10.2, 9.11.x <= 9.11.1, 9.5.x <= 9.5.9 and 10.0.x <= 10.0.0 fail to properly authorize the requests to /api/v4/channels  which allows a User or System Manager, with "Read Groups" permission but with no access for channels to retrieve details about private channels that they were not a member of by sending a request to /api/v4/channels.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-42000
