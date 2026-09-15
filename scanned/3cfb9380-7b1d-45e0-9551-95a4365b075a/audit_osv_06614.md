# [H] BIT-mattermost-2023-3581

## Summary
Severity: High
Advisory: BIT-mattermost-2023-3581
Aliases: CVE-2023-3581
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-3581
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=7.10.0 <7.10.3

## Details
Mattermost fails to properly validate the origin of a websocket connection allowing a MITM attacker on Mattermost to access the websocket APIs.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-3581
