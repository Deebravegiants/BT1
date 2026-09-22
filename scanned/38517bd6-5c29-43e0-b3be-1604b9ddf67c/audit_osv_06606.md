# [M] BIT-mattermost-2022-2366

## Summary
Severity: Medium
Advisory: BIT-mattermost-2022-2366
Aliases: CVE-2022-2366
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2022-2366
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=6.6.0 <6.6.2, >=6.7.0

## Details
Incorrect default configuration for trusted IP header in Mattermost version 6.7.0 and earlier allows attacker to bypass some of the rate limitations in place or use manipulated IPs for audit logging via manipulating the request headers.

## References
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2022-2366
