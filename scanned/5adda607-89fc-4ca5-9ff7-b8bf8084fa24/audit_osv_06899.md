# [H] Post-authentication use-after-free in server-side JavaScript BSON-to-array conversion

## Summary
Severity: High
Advisory: BIT-mongodb-2026-11933
Aliases: CVE-2026-11933
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-11933
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.4

## Details
A use-after-free vulnerability exists in MongoDB Server's server-side JavaScript engine when converting BSON documents to JavaScript arrays. An authenticated user with read privileges who is able to run server-side JavaScript (for example, via $where or $function) can cause the server to access memory that has already been freed. This may result in disclosure of information from the mongod process memory or a denial of service through a server crash.

## References
- https://jira.mongodb.org/browse/SERVER-128125
- https://nvd.nist.gov/vuln/detail/CVE-2026-11933
