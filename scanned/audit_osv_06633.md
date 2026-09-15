# [M] BIT-mattermost-2024-1952

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-1952
Aliases: CVE-2024-1952, GHSA-r4fm-g65h-cr54, GO-2024-2635
Ecosystem: Bitnami
Published: 2024-12-16
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-1952
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=8.1.0 <8.1.9

## Details
Mattermost version 8.1.x before 8.1.9 fails to sanitize data associated with permalinks when a plugin updates an ephemeral post, allowing an authenticated attacker who can control the ephemeral post update to access individual posts' contents in channels they are not a member of.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-1952
