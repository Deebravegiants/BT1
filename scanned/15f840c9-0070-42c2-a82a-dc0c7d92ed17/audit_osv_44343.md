# [M] Query-complexity limit bypass via first/last pagination arguments in AshGraphql enables denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-81636
Aliases: EEF-CVE-2026-81636, GHSA-mwc4-r9fc-h6mg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-81636
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in ash-project ash_graphql allows an unauthenticated client to bypass the configured GraphQL query-complexity limit and force an unbounded database read.

AshGraphql.Graphql.Resolver.query_complexity/3 multiplies child complexity by the requested page size only when the argument map contains :limit (offset pagination). Relay connections and keyset pagination use first and last, which never match that clause and fall through to the catch-all that returns child_complexity + 1. A nested relay query such as posts(first: 500) { edges { node { comments(first: 500) { ... } } } } therefore scores as trivially cheap while materializing the full fan-out, passing an Absinthe max_complexity cap that rejects the equivalent limit-based query. The fix adds first and last clauses clamped to the action's page size.

This issue affects ash_graphql: from 0.16.23 before 1.11.0.

## References
- https://cna.erlef.org/cves/CVE-2026-81636.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-81636
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81636.json
- https://github.com/ash-project/ash_graphql/security/advisories/GHSA-mwc4-r9fc-h6mg
- https://nvd.nist.gov/vuln/detail/CVE-2026-81636
- https://github.com/ash-project/ash_graphql/commit/c3229f6a65cbabb32fd7ffcac881922d1b3b30ad
- https://github.com/ash-project/ash_graphql
