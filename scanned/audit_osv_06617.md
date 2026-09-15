# [M] BIT-mattermost-2023-3586

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-3586
Aliases: CVE-2023-3586
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-3586
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=7.10.0 <7.10.3

## Details
Mattermost fails to disable public Boards after the "Enable Publicly-Shared Boards" configuration option is disabled, resulting in previously-shared public Boards to remain accessible.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-3586
