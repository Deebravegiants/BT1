# [C] Saltcorn: SQL Injection via Unparameterized Sync Endpoints (maxLoadedId)

## Summary
Severity: Critical
Advisory: GHSA-jp74-mfrx-3qvh
CVE: CVE-2026-41478
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-jp74-mfrx-3qvh
Type: github-advisory

## Affected
- npm: `@saltcorn/server` — affected >=0 <1.4.6
- npm: `@saltcorn/server` — affected >=1.5.0-beta.0 <1.5.6
- npm: `@saltcorn/server` — affected >=1.6.0-alpha.0 <1.6.0-beta.5

## Details
### Summary
A critical SQL injection vulnerability in Saltcorn’s mobile-sync routes allows any authenticated low-privilege user with read access to at least one table to inject arbitrary SQL through sync parameters. This can lead to full database exfiltration, including admin password hashes and configuration secrets, and may also enable database modification or destruction depending on the backend. 

### Details
The issue affects the mobile-sync endpoints:

- `POST /sync/load_changes`
- `POST /sync/deletes`

According to the provided analysis, user-controlled values from the request body are interpolated directly into SQL template literals without parameterization, type enforcement, or sanitization. In particular, `req.body.syncInfos[tableName].maxLoadedId` is embedded into SQL in `getSyncRows()` and timestamp-derived values are similarly interpolated in `getDelRows()`. 

Relevant vulnerable code paths include:

- `packages/server/routes/sync.js` — `getSyncRows()`
  - branch using `where data_tbl."${db.sqlsanitize(pkName)}" > ${syncInfo.maxLoadedId}`
  - branch using `and info_tbl.ref > ${syncInfo.maxLoadedId}`
- `packages/server/routes/sync.js` — `getDelRows()`
  - timestamp expressions built from request-controlled values and inserted into SQL
- `packages/server/routes/sync.js` — `/load_changes` route handler
  - request body fields are passed into the SQL-building functions without validation or safe binding

The root cause is that values are treated as trusted SQL fragments rather than bound parameters. While `db.sqlsanitize()` is used for identifiers elsewhere, that does not protect interpolated values and is not intended to prevent value-based SQL injection. The report notes there is no `parseInt()`, numeric validation, or prepared-statement binding before these values are concatenated into the query string. 

This means a normal authenticated user can escape the intended query logic and execute arbitrary SQL in the context of the application database. The provided evidence demonstrates successful extraction of user records and schema information through the vulnerable sync route, confirming that the injection is practically exploitable. 

### PoC
Based on the provided report, the issue can be reproduced by authenticating as a normal user, sending a crafted request to the affected sync endpoint, and placing a malicious SQL expression into the sync metadata field that is later interpolated into the backend query. Successful exploitation returns attacker-selected database contents in the sync response. 

### Impact
- **Type:** SQL injection
- **Who is impacted:** Any Saltcorn deployment exposing the affected mobile-sync routes to authenticated users
- **Security impact:** An authenticated low-privilege user may exfiltrate the full database, including password hashes, configuration secrets, application data, and schema information; on some backends, the same flaw may also permit writes, schema changes, or destructive operations
- **Attack preconditions:** The attacker needs a valid authenticated account with access to at least one readable table through the sync feature
- **Privilege impact:** The issue allows escalation from normal user access to database-wide compromise

## References
- https://github.com/saltcorn/saltcorn/security/advisories/GHSA-jp74-mfrx-3qvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-41478
- https://github.com/saltcorn/saltcorn
