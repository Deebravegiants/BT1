# [M] BIT-mattermost-2024-47145

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-47145
Aliases: CVE-2024-47145
Ecosystem: Bitnami
Published: 2024-09-27
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-47145
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.5.0 <9.5.9

## Details
Mattermost versions 9.5.x <= 9.5.8 fail to properly authorize access to archived channels when viewing archived channels is disabled, which allows an attacker to view posts and files of archived channels via file links.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-47145
