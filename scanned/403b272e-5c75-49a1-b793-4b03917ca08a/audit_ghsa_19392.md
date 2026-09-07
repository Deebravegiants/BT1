# [H] Apollo Router Query Planner Vulnerable to Excessive Resource Consumption via Optimization Bypass

## Summary
Severity: High
Advisory: GHSA-94hh-jmq8-2fgp
CVE: CVE-2025-32032
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-94hh-jmq8-2fgp
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=0 <1.61.2
- crates.io: `apollo-router` — affected >=2.0.0-alpha.0 <2.1.1

## Details
# Impact

## Summary

A vulnerability in Apollo Router allowed queries with deeply nested and reused named fragments to be prohibitively expensive to query plan, specifically due to internal optimizations being frequently bypassed. This could lead to excessive resource consumption and denial of service.

## Details

The query planner includes an optimization that significantly speeds up planning for applicable GraphQL selections. However, queries with deeply nested and reused named fragments can generate many selections where this optimization does not apply, leading to significantly longer planning times. Because the query planner does not enforce a timeout, a small number of such queries can exhaust router's thread pool, rendering it inoperable.

## Fix/Mitigation

- A new **Query Optimization Limit** metric has been added:
  - This metric approximates the number of selections that cannot be skipped by the existing optimization.
  - The metric is checked against a limit to prevent excessive computation.

Given the complexity of query planning optimizations, we will continue refining these solutions based on real-world performance and accuracy tests.

# Patches

This has been remediated in `apollo-router` versions 1.61.2 and 2.1.1.

# Workarounds

The only known workaround is "Safelisting" or "Safelisting with IDs only" per [Safelisting with Persisted Queries - Apollo GraphQL Docs](https://www.apollographql.com/docs/graphos/routing/security/persisted-queries#router-security-levels).

# References

[Query Planning Documentation](https://www.apollographql.com/docs/graphos/reference/federation/query-plans)

## Acknowledgements

We appreciate the efforts of the security community in identifying and improving the performance and security of query planning mechanisms.

## References
- https://github.com/apollographql/router/security/advisories/GHSA-94hh-jmq8-2fgp
- https://nvd.nist.gov/vuln/detail/CVE-2025-32032
- https://github.com/apollographql/router/commit/ab6675a63174715ea6ff50881fc957831d4e9564
- https://github.com/apollographql/router/commit/bba032e183b861348a466d3123c7137a1ae18952
- https://github.com/apollographql/router
