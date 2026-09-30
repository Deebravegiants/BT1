# [M] BIT-mattermost-2024-36250

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-36250
Aliases: CVE-2024-36250
Ecosystem: Bitnami
Published: 2024-11-15
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-36250
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.11.0 <9.11.3

## Details
Mattermost versions 9.11.x <= 9.11.2, and 9.5.x <= 9.5.10 fail to protect the mfa code against replay attacks, which allows an attacker to reuse the MFA code within ~30 seconds

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-36250
