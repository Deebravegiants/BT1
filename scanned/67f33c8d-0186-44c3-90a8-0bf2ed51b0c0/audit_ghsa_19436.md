# [H] Apollo Router Operation Limits Vulnerable to Bypass via Integer Overflow

## Summary
Severity: High
Advisory: GHSA-84m6-5m72-45fp
CVE: CVE-2025-32033
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-84m6-5m72-45fp
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=0 <1.61.2
- crates.io: `apollo-router` — affected >=2.0.0-alpha.0 <2.1.1

## Details
# Impact

## Summary

A vulnerability in Apollo Router allowed certain queries to bypass configured operation limits, specifically due to integer overflow.

## Details

The operation limits plugin uses unsigned 32-bit integers to track limit counters (e.g. for a query's height). If a counter exceeded the maximum value for this data type (4,294,967,295), it wrapped around to 0, unintentionally allowing queries to bypass configured thresholds. This could occur for large queries if the payload limit were sufficiently increased, but could also occur for small queries with deeply nested and reused named fragments.

## Fix/Mitigation

Logic was updated to ensure counter overflow is handled correctly and does not wrap around to 0.

# Patches

This has been remediated in `apollo-router` versions 1.61.2 and 2.1.1.

# Workarounds

The only known workaround is "Safelisting" or "Safelisting with IDs only" per [Safelisting with Persisted Queries - Apollo GraphQL Docs](https://www.apollographql.com/docs/graphos/routing/security/persisted-queries#router-security-levels).

## Acknowledgements

We appreciate the efforts of the security community in identifying and improving the performance and security of operation limiting mechanisms.

## References
- https://github.com/apollographql/router/security/advisories/GHSA-84m6-5m72-45fp
- https://nvd.nist.gov/vuln/detail/CVE-2025-32033
- https://github.com/apollographql/router/commit/ab6675a63174715ea6ff50881fc957831d4e9564
- https://github.com/apollographql/router/commit/bba032e183b861348a466d3123c7137a1ae18952
- https://github.com/apollographql/router
