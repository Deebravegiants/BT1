# [H] BIT-mattermost-2023-4478

## Summary
Severity: High
Advisory: BIT-mattermost-2023-4478
Aliases: CVE-2023-4478
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-4478
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=7.9.0 <7.10.5, >=8.0.0

## Details
Mattermost fails to restrict which parameters' values it takes from the request during signup allowing an attacker to register users as inactive, thus blocking them from later accessing Mattermost without the system admin activating their accounts.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-4478
