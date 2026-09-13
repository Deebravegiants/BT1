# [M] Race condition in privilege cache invalidation cycle

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-6707
Aliases: CVE-2025-6707
Ecosystem: Bitnami
Published: 2025-09-16
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-6707
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.5

## Details
Under certain conditions, an authenticated user request may execute with stale privileges following an intentional change by an authorized administrator. This issue affects MongoDB Server v5.0 version prior to 5.0.31, MongoDB Server v6.0 version prior to 6.0.24, MongoDB Server v7.0 version prior to 7.0.21 and MongoDB Server v8.0 version prior to 8.0.5.

## References
- https://jira.mongodb.org/browse/SERVER-93497
- https://nvd.nist.gov/vuln/detail/CVE-2025-6707
