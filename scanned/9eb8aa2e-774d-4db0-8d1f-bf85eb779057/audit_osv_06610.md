# [H] BIT-mattermost-2023-1831

## Summary
Severity: High
Advisory: BIT-mattermost-2023-1831
Aliases: CVE-2023-1831
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-1831
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=7.8.0 <7.8.2, >=7.9.0

## Details
Mattermost fails to redact from audit logs the user password during user creation and the user password hash in other operations if the experimental audit logging configuration was enabled (ExperimentalAuditSettings section in config).

## References
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2023-1831
