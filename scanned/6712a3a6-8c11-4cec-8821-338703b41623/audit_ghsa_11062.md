# [C] Parse Server vulnerable to SQL Injection via dot-notation sub-key name in `Increment` operation on PostgreSQL

## Summary
Severity: Critical
Advisory: GHSA-gqpp-xgvh-9h7h
CVE: CVE-2026-31871
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-gqpp-xgvh-9h7h
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.6.0-alpha.5
- npm: `parse-server` — affected >=0 <8.6.31

## Details
### Impact

A SQL injection vulnerability exists in the PostgreSQL storage adapter when processing `Increment` operations on nested object fields using dot notation (e.g., `stats.counter`). The sub-key name is interpolated directly into SQL string literals without escaping. An attacker who can send write requests to the Parse Server REST API can inject arbitrary SQL via a crafted sub-key name containing single quotes, potentially executing commands or reading data from the database, bypassing CLPs and ACLs.

Only Postgres deployments are affected.

### Patches

The fix escapes single quotes in the sub-key name before interpolating it into the SQL query, preventing breakout from SQL string literals.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-gqpp-xgvh-9h7h
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.5
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.31

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-gqpp-xgvh-9h7h
- https://nvd.nist.gov/vuln/detail/CVE-2026-31871
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.31
- https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.5
