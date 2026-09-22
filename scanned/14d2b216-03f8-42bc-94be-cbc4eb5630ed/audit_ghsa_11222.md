# [M] NocoDB Vulnerable to SQL Injection via DATEADD Formula

## Summary
Severity: Medium
Advisory: GHSA-45rp-9p97-h852
CVE: CVE-2026-28399
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-45rp-9p97-h852
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.301.3

## Details
### Summary
An authenticated user with Creator role can inject arbitrary SQL via the DATEADD formula's unit parameter.

### Details
The third argument (unit) of `DATEADD` was interpolated directly into `knex.raw()` queries after only stripping quote characters. Validation in `formulas.ts` only checked `Literal` AST node types — non-Literal types bypassed validation entirely. Affected MySQL, PostgreSQL, and SQLite function mappings.

### Impact
SQL injection allowing data exfiltration or modification, scoped to the connected database.

### Credit
This issue was reported by [@q1uf3ng](https://github.com/q1uf3ng).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-45rp-9p97-h852
- https://nvd.nist.gov/vuln/detail/CVE-2026-28399
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/0.301.3
