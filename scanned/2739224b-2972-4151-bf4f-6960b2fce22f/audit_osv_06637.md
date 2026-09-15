# [M] BIT-mattermost-2024-24776

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-24776
Aliases: CVE-2024-24776, GHSA-r833-w756-h5p2, GO-2024-2566
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-24776
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <9.6.1

## Details
Mattermost fails to check the required permissions in the POST /api/v4/channels/stats/member_count API resulting in channel member counts being leaked to a user without permissions.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-24776
