# [H] Improper neutralization of null bytes may lead to buffer over-reads in MongoDB Server

## Summary
Severity: High
Advisory: BIT-mongodb-2024-10921
Aliases: CVE-2024-10921
Ecosystem: Bitnami
Published: 2025-10-02
Source: https://osv.dev/vulnerability/BIT-mongodb-2024-10921
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.3

## Details
An authorized user may trigger crashes or receive the contents of buffer over-reads of Server memory by issuing specially crafted requests that construct malformed BSON in the MongoDB Server. This issue affects MongoDB Server v5.0 versions prior to 5.0.30 , MongoDB Server v6.0 versions prior to 6.0.19, MongoDB Server v7.0 versions prior to 7.0.15 and MongoDB Server v8.0 versions prior to and including 8.0.2.

## References
- https://jira.mongodb.org/browse/SERVER-96419
- https://nvd.nist.gov/vuln/detail/CVE-2024-10921
