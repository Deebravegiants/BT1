# [M] BIT-mattermost-2023-2281

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-2281
Aliases: CVE-2023-2281
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-2281
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <7.9.0

## Details
When archiving a team, Mattermost fails to sanitize the related Websocket event sent to currently connected clients. This allows the clients to see the name, display name, description, and other data about the archived team.

## References
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2023-2281
