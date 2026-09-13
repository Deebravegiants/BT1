# [M] Flaw in the updateUser Command May Allow Unauthorized Configuration Change

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-6915
Aliases: CVE-2026-6915
Ecosystem: Bitnami
Published: 2026-05-08
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-6915
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.7

## Details
An authorization flaw in the user management command could allow an authenticated user to make limited changes to authentication-related data associated with another user account. This could affect how authentication is performed for the impacted account.

## References
- https://jira.mongodb.org/browse/SERVER-119679
- https://nvd.nist.gov/vuln/detail/CVE-2026-6915
