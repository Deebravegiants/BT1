# [H] Use-After-Free in MongoDB FLE Query Analysis When Processing Positional Projections on Encrypted Fields

## Summary
Severity: High
Advisory: BIT-mongodb-2026-8201
Aliases: CVE-2026-8201
Ecosystem: Bitnami
Published: 2026-05-14
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-8201
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.2

## Details
A use-after-free vulnerability exists in MongoDB's Field-Level Encryption (FLE) query analysis component, affecting client-side uses of mongocryptd and crypt_shared. Triggering this vulnerability requires control over the structure of a client's FLE-related query.

This issue impacts MongoDB Server’s mongocryptd component v7.0 versions prior to 7.0.34, v8.0 versions prior to 8.0.23, v8.2 versions prior to 8.2.9 and v8.3 versions prior to 8.3.2.

## References
- https://jira.mongodb.org/browse/SERVER-122032
- https://nvd.nist.gov/vuln/detail/CVE-2026-8201
