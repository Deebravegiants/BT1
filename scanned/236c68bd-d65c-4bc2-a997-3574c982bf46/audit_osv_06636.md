# [H] BIT-mattermost-2024-2450

## Summary
Severity: High
Advisory: BIT-mattermost-2024-2450
Aliases: CVE-2024-2450
Ecosystem: Bitnami
Published: 2024-12-16
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-2450
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.4.0 <9.4.3, >=9.5.0

## Details
Mattermost versions 8.1.x before 8.1.10, 9.2.x before 9.2.6, 9.3.x before 9.3.2, and 9.4.x before 9.4.3 fail to correctly verify account ownership when switching from email to SAML authentication, allowing an authenticated attacker to take over other user accounts via a crafted switch request under specific conditions.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-2450
