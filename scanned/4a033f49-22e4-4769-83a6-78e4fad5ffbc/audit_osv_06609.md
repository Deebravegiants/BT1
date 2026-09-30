# [M] BIT-mattermost-2023-1775

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-1775
Aliases: CVE-2023-1775, GHSA-8jhh-3jf2-pfwr
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-1775
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <7.1.6, >=7.7.1

## Details
When running in a High Availability configuration, Mattermost fails to sanitize some of the user_updated and post_deleted events broadcast to all users, leading to disclosure of sensitive information to some of the users with currently connected Websocket clients.

## References
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2023-1775
