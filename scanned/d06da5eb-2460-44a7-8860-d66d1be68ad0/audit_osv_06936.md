# [H] Post-auth memory exhaustion via bitwise match expressions

## Summary
Severity: High
Advisory: BIT-mongodb-2026-8199
Aliases: CVE-2026-8199
Ecosystem: Bitnami
Published: 2026-05-14
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-8199
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.2

## Details
An authenticated user can cause excess memory usage via bitwise match expression AST processing of $bitsAllSet, $bitsAnySet, $bitsAllClear, and $bitsAnyClear. This contributes to memory pressure and may lead to availability loss by OOM.

This issue impacts MongoDB Server v7.0 versions prior to 7.0.34, v8.0 versions prior to 8.0.23, v8.2 versions prior to 8.2.9 and v8.3 versions prior to 8.3.2.

## References
- https://jira.mongodb.org/browse/SERVER-122449
- https://nvd.nist.gov/vuln/detail/CVE-2026-8199
