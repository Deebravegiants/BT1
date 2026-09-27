# [M] BIT-mattermost-2023-3582

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-3582
Aliases: CVE-2023-3582
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-3582
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=7.10.0 <7.10.3

## Details
Mattermost fails to verify channel membership when linking a board to a channel allowing a low-privileged authenticated user to link a Board to a private channel they don't have access to,

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-3582
