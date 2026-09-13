# [M] BIT-mattermost-2023-5333

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-5333
Aliases: CVE-2023-5333
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-5333
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=8.1.0 <8.1.2

## Details
Mattermost fails to deduplicate input IDs allowing a simple user to cause the application to consume excessive resources and possibly crash by sending a specially crafted request to /api/v4/users/ids with multiple identical IDs.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-5333
