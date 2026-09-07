# [C] Parse Server vulnerable to SQL injection via `Increment` operation on nested object field in PostgreSQL

## Summary
Severity: Critical
Advisory: GHSA-q3vj-96h2-gwvg
CVE: CVE-2026-31856
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-q3vj-96h2-gwvg
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.6.0-alpha.3
- npm: `parse-server` — affected >=0 <8.6.29

## Details
### Impact

A SQL injection vulnerability exists in the PostgreSQL storage adapter when processing `Increment` operations on nested object fields using dot notation (e.g., `stats.counter`). The `amount` value is interpolated directly into the SQL query without parameterization or type validation. An attacker who can send write requests to the Parse Server REST API can inject arbitrary SQL subqueries to read any data from the database, bypassing CLPs and ACLs.

MongoDB deployments are not affected.

### Patches

The fix adds type validation to reject non-number values and parameterizes the value in the SQL query instead of interpolating it.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-q3vj-96h2-gwvg
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.3
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.29

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-q3vj-96h2-gwvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-31856
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.29
- https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.3
