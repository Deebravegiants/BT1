# [M] BIT-mattermost-2024-28053

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-28053
Aliases: CVE-2024-28053, GHSA-qqc8-rv37-79q5, GO-2024-3334
Ecosystem: Bitnami
Published: 2024-12-16
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-28053
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=8.1.0 <8.1.10

## Details
Resource Exhaustion in Mattermost Server versions 8.1.x before 8.1.10 fails to limit the size of the payload that can be read and parsed allowing an attacker to send a very large email payload and crash the server.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-28053
