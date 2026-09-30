# [M] BIT-mattermost-2024-45835

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-45835
Aliases: CVE-2024-45835, GHSA-xgq9-7gw6-jr5r
Ecosystem: Bitnami
Published: 2024-09-18
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-45835
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <5.9.0

## Details
Mattermost Desktop App versions <=5.8.0 fail to sufficiently configure Electron Fuses which allows an attacker to gather Chromium cookies or abuse other misconfigurations via remote/local access.

## References
- https://mattermost.com/security-updates
