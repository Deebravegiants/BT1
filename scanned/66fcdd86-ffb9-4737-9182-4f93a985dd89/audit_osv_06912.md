# [M] MongoDB mongos Improper Authorization Check in Cursor Termination Allowing Cross-Database Privilege Misuse

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-13068
Aliases: CVE-2026-13068
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13068
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An authenticated user holding cursor termination privileges on one database may incorrectly be permitted to terminate active cursors on a separate database, disrupting ongoing query operations for other users. The behavior stems from an authorization check that does not correctly scope privileges to the appropriate namespace.

## References
- https://jira.mongodb.org/browse/SERVER-128198
- https://nvd.nist.gov/vuln/detail/CVE-2026-13068
