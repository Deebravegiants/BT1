# [H] BIT-mattermost-2023-45847

## Summary
Severity: High
Advisory: BIT-mattermost-2023-45847
Aliases: CVE-2023-45847
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-45847
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.2.0 <9.2.2

## Details
Mattermost fails to to check the length when setting the title in a run checklist in Playbooks, allowing an attacker to send a specially crafted request and crash the Playbooks plugin

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-45847
