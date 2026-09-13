# [M] NocoDB: SQL Injection via Column Title in Bulk GroupBy

## Summary
Severity: Medium
Advisory: GHSA-p8wx-5f39-w3x4
CVE: CVE-2026-47384
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-p8wx-5f39-w3x4
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.05.1

## Details
### Summary
An authenticated user with column-create permission can inject SQL into the bulk groupBy
endpoint by setting a column's title to a SQL fragment.

### Details
The bulk groupBy path in `group-by.ts` builds three database-specific `knex.raw()`
aggregations that interpolate the request's `column_name` directly into the SQL string.
Column lookup in `data-table.service.ts` matches on both the sanitized `column_name`
field and the free-text `title`, so a title containing a SQL fragment bypasses the
public endpoint's existing column allowlist and reaches the query builder unescaped.

### Impact
SQL injection against the connected database with read access to any expression an
attacker can place in a column title. Exploitation requires an authenticated session
with permission to create or rename columns.

### Credit
This issue was reported by [@geo-chen](https://github.com/geo-chen).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-p8wx-5f39-w3x4
- https://nvd.nist.gov/vuln/detail/CVE-2026-47384
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.05.1
