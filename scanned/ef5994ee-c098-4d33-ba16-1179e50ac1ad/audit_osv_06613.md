# [M] BIT-mattermost-2023-3577

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-3577
Aliases: CVE-2023-3577
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-3577
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=7.10.0 <7.10.3

## Details
Mattermost fails to properly restrict requests to localhost/intranet during the interactive dialog, which could allow an attacker to perform a limited blind SSRF.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-3577
