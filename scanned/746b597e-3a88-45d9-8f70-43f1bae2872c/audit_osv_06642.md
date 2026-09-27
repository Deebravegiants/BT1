# [M] BIT-mattermost-2024-42406

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-42406
Aliases: CVE-2024-42406
Ecosystem: Bitnami
Published: 2024-10-02
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-42406
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.10.0 <9.10.2, >=9.11.0

## Details
Mattermost versions 9.11.x <= 9.11.0, 9.10.x <= 9.10.1, 9.9.x <= 9.9.2 and 9.5.x <= 9.5.8 fail to properly authorize requests when viewing archived channels is disabled, which allows an attacker to retrieve post and file information about archived channels. Examples are flagged or unread posts as well as files.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-42406
