# [M] Parse Server allows public `explain` queries which may expose sensitive database performance information and schema details

## Summary
Severity: Medium
Advisory: GHSA-7cx5-254x-cgrq
CVE: CVE-2025-64502
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-7cx5-254x-cgrq
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <8.5.0-alpha.5

## Details
### Impact

The MongoDB `explain()` method provides detailed information about query execution plans, including index usage, collection scanning behavior, and performance metrics. Parse Server permits any client to execute explain queries without requiring the master key. This exposes:

- Database schema structure and field names
- Index configurations and query optimization details
- Query execution statistics and performance metrics
- Potential attack vectors for database performance exploitation

### Patches

A new `databaseOptions.allowPublicExplain` configuration option has been introduced that allows to restrict `explain` queries to the master key. The option defaults to `true` for now to avoid a breaking change in production systems that depends on public `explain` availability. In addition, a security warning is logged when the option is not explicitly set, or set to `true`. In a future major release of Parse Server, the default will change to `false`.

### Workarounds

Implementing middleware to block explain queries from non-master-key requests, or monitor and alert on explain query usage in production environments.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-7cx5-254x-cgrq
- https://nvd.nist.gov/vuln/detail/CVE-2025-64502
- https://github.com/parse-community/parse-server/pull/9890
- https://github.com/parse-community/parse-server/commit/4456b02280c2d8dd58b7250e9e67f1a8647b3452
- https://github.com/parse-community/parse-server
