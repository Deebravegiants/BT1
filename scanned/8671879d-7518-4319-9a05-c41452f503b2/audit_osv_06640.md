# [M] BIT-mattermost-2024-39837

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-39837
Aliases: CVE-2024-39837, GHSA-vvpg-55p7-5h8w, GO-2024-3032
Ecosystem: Bitnami
Published: 2024-09-05
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-39837
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.5.0 <9.5.7, >=9.9.0

## Details
Mattermost versions 9.9.x <= 9.9.0, 9.5.x <= 9.5.6 fail to properly restrict channel creation which allows a malicious remote to create arbitrary channels, when shared channels were enabled.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-39837
