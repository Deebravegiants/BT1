# [H] Local File Disclosure in MongoDB Server via MozJS Scripting Engine Module Loader

## Summary
Severity: High
Advisory: BIT-mongodb-2026-13078
Aliases: CVE-2026-13078
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13078
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
A vulnerability was discovered in MongoDB Server where the server-side MozJS scripting engine unconditionally registered a module loading hook that enables JavaScript calls to read arbitrary files from the host filesystem using the mongod process's privileges. An authenticated user could exploit this through crafted aggregation pipeline commands to read sensitive files accessible to the MongoDB server process.

## References
- https://jira.mongodb.org/browse/SERVER-128832
- https://nvd.nist.gov/vuln/detail/CVE-2026-13078
