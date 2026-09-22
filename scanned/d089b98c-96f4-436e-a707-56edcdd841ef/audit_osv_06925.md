# [H] Mongod can run out of stack memory when expressions create deeply nested documents

## Summary
Severity: High
Advisory: BIT-mongodb-2026-1849
Aliases: CVE-2026-1849
Ecosystem: Bitnami
Published: 2026-02-26
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-1849
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.2

## Details
MongoDB Server may experience an out-of-memory failure while evaluating expressions that produce deeply nested documents. The issue arises in recursive functions because the server does not periodically check the depth of the expression.

## References
- https://jira.mongodb.org/browse/SERVER-102364
- https://nvd.nist.gov/vuln/detail/CVE-2026-1849
