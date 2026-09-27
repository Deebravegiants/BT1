# [H] Apollo Router Query Planner Vulnerable to Excessive Resource Consumption via Named Fragment Expansion

## Summary
Severity: High
Advisory: GHSA-75m2-jhh5-j5g2
CVE: CVE-2025-32034
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-75m2-jhh5-j5g2
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=0 <1.61.2
- crates.io: `apollo-router` — affected >=2.0.0-alpha.0 <2.1.1

## Details
# Impact

## Summary

A vulnerability in Apollo Router allowed queries with deeply nested and reused named fragments to be prohibitively expensive to query plan, specifically during named fragment expansion. This could lead to excessive resource consumption and denial of service.

## Details

Named fragments were being expanded once per fragment spread during query planning, leading to exponential resource usage when deeply nested and reused fragments were involved.

## Fix/Mitigation

A new **Query Fragment Expansion Limit** metric has been introduced:
  - This metric computes the number of selections a query would have if its fragment spreads were fully expanded.
  - The metric is checked against a limit to prevent excessive computation.

# Patches

This has been remediated in `apollo-router` versions 1.61.2 and 2.1.1.

# Workarounds

The only known workaround is "Safelisting" or "Safelisting with IDs only" per [Safelisting with Persisted Queries - Apollo GraphQL Docs](https://www.apollographql.com/docs/graphos/routing/security/persisted-queries#router-security-levels).

# References

[Query Planning Documentation](https://www.apollographql.com/docs/graphos/reference/federation/query-plans)

## Acknowledgements

We appreciate the efforts of the security community in identifying and improving the performance and security of query planning mechanisms.

## References
- https://github.com/apollographql/router/security/advisories/GHSA-75m2-jhh5-j5g2
- https://nvd.nist.gov/vuln/detail/CVE-2025-32034
- https://github.com/apollographql/router/commit/ab6675a63174715ea6ff50881fc957831d4e9564
- https://github.com/apollographql/router/commit/bba032e183b861348a466d3123c7137a1ae18952
- https://github.com/apollographql/router
