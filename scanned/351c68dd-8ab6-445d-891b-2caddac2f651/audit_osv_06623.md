# [H] BIT-mattermost-2023-49607

## Summary
Severity: High
Advisory: BIT-mattermost-2023-49607
Aliases: CVE-2023-49607
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-49607
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.2.0 <9.2.2

## Details
Mattermost fails to validate the type of the "reminder" body request parameter allowing an attacker to crash the Playbook Plugin when updating the status dialog.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-49607
