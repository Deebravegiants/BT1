# [M] TypeORM 0.2.21 through 1.1.0 SQL Injection via SelectQueryBuilder.distinctOn

## Summary
Severity: Medium
Advisory: CVE-2026-76848
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-76848
Type: osv

## Details
TypeORM's SelectQueryBuilder.distinctOn accepts an array of strings and stores it on the expression map without validation. For PostgreSQL-family drivers, createSelectDistinctExpression in src/query-builder/SelectQueryBuilder.ts joins that array and interpolates the result into the generated statement as SELECT DISTINCT ON (values), with no escaping, quoting, identifier validation or allowlist, and without routing the values through replacePropertyNames or the driver's escape helper. Because the interpolation point is a parenthesized SQL expression list rather than an identifier-only position, a supplied element may carry arbitrary expressions, including correlated subqueries. An application that forwards a client-controlled value into distinctOn, for instance to let a caller choose a deduplication column, allows that client to read data anywhere the application's database role can reach through boolean or time-based inference, independently of the entity being queried. validateOrderByCondition, the allowlist check guarding the orderBy family in the same class, is not applied to this path.

## References
- https://www.npmjs.com/package/typeorm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76848.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76848
- https://www.vulncheck.com/advisories/typeorm-through-sql-injection-via-selectquerybuilder-distincton
- https://github.com/typeorm/typeorm
- https://github.com/typeorm/typeorm/blob/1.1.0/src/query-builder/SelectQueryBuilder.ts
