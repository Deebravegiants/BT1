# [H] Post-authentication use-after-free error in $_internalJsEmit and mapreduce commands

## Summary
Severity: High
Advisory: BIT-mongodb-2026-8336
Aliases: CVE-2026-8336
Ecosystem: Bitnami
Published: 2026-05-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-8336
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.2

## Details
After invoking $_internalJsEmit, which is not intended to be directly accessible, or mapreduce command’s map function in a certain way, an authenticated user can subsequently crash mongod when the server-side JavaScript engine (through $where, $function, mapreduce reduce stage, etc.) is used also in a specific way, resulting in a post-authentication denial-of-service.

This issue impacts MongoDB Server v8.2 versions prior to 8.2.9 and v8.3 versions prior to 8.3.2.

## References
- https://jira.mongodb.org/browse/SERVER-121610
- https://nvd.nist.gov/vuln/detail/CVE-2026-8336
