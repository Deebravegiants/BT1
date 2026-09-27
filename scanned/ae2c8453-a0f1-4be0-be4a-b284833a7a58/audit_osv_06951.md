# [M] Sensitive data could be written to mongod.log

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-9751
Aliases: CVE-2026-9751
Ecosystem: Bitnami
Published: 2026-06-13
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9751
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
The ldapQueryPassword parameter, when set through the runtime setParameter command, will log the new password to the mongod.log file in plain text.

## References
- https://jira.mongodb.org/browse/SERVER-123370
- https://nvd.nist.gov/vuln/detail/CVE-2026-9751
