# [M] BIT-mattermost-2023-5331

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-5331
Aliases: CVE-2023-5331
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-5331
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=8.1.0 <8.1.2

## Details
Mattermost fails to properly check the creator of an attached file when adding the file to a draft post, potentially exposing unauthorized file information.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-5331
