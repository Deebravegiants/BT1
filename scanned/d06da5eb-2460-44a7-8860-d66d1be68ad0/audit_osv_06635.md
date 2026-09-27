# [M] BIT-mattermost-2024-2446

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-2446
Aliases: CVE-2024-2446
Ecosystem: Bitnami
Published: 2024-12-16
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-2446
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.4.0 <9.4.3

## Details
Mattermost versions 8.1.x before 8.1.10, 9.2.x before 9.2.6, 9.3.x before 9.3.2, and 9.4.x before 9.4.3 fail to limit the number of @-mentions processed per message, allowing an authenticated attacker to crash the client applications of other users via large, crafted messages.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-2446
