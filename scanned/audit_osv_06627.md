# [H] BIT-mattermost-2023-5330

## Summary
Severity: High
Advisory: BIT-mattermost-2023-5330
Aliases: CVE-2023-5330
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-5330
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=8.1.0 <8.1.2

## Details
Mattermost fails to enforce a limit for the size of the cache entry for  OpenGraph data allowing an attacker to send a specially crafted request to the /api/v4/opengraph filling the cache and turning the server unavailable.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-5330
