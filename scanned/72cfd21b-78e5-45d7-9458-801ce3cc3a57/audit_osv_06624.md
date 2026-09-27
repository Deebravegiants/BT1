# [M] BIT-mattermost-2023-49809

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-49809
Aliases: CVE-2023-49809
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-49809
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.0.0 <9.1.1

## Details
Mattermost fails to handle a null request body in the /add endpoint, allowing a simple member to send a request with null request body to that endpoint and make it crash. After a few repetitions, the plugin is disabled.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-49809
