# [H] Authenticate command with specific mechanism parameter can trigger server crash

## Summary
Severity: High
Advisory: BIT-mongodb-2026-9742
Aliases: CVE-2026-9742
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9742
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
When OIDC authentication is enabled in configuration, clients may set specific values in the "mechanism" parameter of the "authenticate" command that lead to server crash. The authenticate command is accessible to unauthenticated clients, leading to pre-auth denial-of-service in affected product configurations.

## References
- https://jira.mongodb.org/browse/SERVER-124183
- https://nvd.nist.gov/vuln/detail/CVE-2026-9742
