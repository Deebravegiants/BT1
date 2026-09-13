# [H] Client side encryption fails to encrypt values in a $vectorSearch

## Summary
Severity: High
Advisory: BIT-mongodb-2026-9741
Aliases: CVE-2026-9741
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-9741
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.3

## Details
A bug in query analysis processing of the $vectorSearch aggregation stage for Queryable Encryption (QE) or Client-Side Field Level Encryption (CSFLE)  results in literal values for encrypted fields within the $vectorSearch stage filter expressions to be sent to the server as plaintext instead of ciphertext.

## References
- https://jira.mongodb.org/browse/SERVER-123507
- https://nvd.nist.gov/vuln/detail/CVE-2026-9741
