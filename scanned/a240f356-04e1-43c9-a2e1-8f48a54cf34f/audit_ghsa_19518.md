# [H] Apollo Router Query Validation Vulnerable to Excessive Resource Consumption via Named Fragment Processing

## Summary
Severity: High
Advisory: GHSA-3j43-9v8v-cp3f
CVE: CVE-2025-32380
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-3j43-9v8v-cp3f
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=0 <1.61.2
- crates.io: `apollo-router` — affected >=2.0.0-alpha.0 <2.1.1

## Details
# Impact

## Summary

A vulnerability in Apollo Router's usage of Apollo Compiler allowed queries with deeply nested and reused named fragments to be prohibitively expensive to validate. This could lead to excessive resource consumption and denial of service.

## Details

Named fragments were being processed once per fragment spread in some cases during query validation, leading to exponential resource usage when deeply nested and reused fragments were involved.

## Fix/Mitigation

Apollo Router's usage of Apollo Compiler has been updated so that validation logic processes each named fragment only once, preventing redundant traversal.

# Patches

This has been remediated in `apollo-router` versions 1.61.2 and 2.1.1.

# Workarounds
The only known workaround is "Safelisting with IDs only" per [Safelisting with Persisted Queries - Apollo GraphQL Docs](https://www.apollographql.com/docs/graphos/routing/security/persisted-queries#router-security-levels). The "Safelisting" security level is not sufficient, since that level allows freeform GraphQL queries to be sent to Apollo Router.

# References 
[Query Planning Documentation](https://www.apollographql.com/docs/graphos/reference/federation/query-plans)

## Acknowledgements
We appreciate the efforts of the security community in identifying and improving the performance and security of query validation mechanisms.

## References
- https://github.com/apollographql/router/security/advisories/GHSA-3j43-9v8v-cp3f
- https://nvd.nist.gov/vuln/detail/CVE-2025-32380
- https://github.com/apollographql/router/commit/ab6675a63174715ea6ff50881fc957831d4e9564
- https://github.com/apollographql/router/commit/bba032e183b861348a466d3123c7137a1ae18952
- https://github.com/apollographql/router
