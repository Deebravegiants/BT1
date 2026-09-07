# [H] strawberry-graphql: Denial of Service via unbounded WebSocket subscriptions

## Summary
Severity: High
Advisory: GHSA-hv3w-m4g2-5x77
CVE: CVE-2026-35526
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-hv3w-m4g2-5x77
Type: github-advisory

## Affected
- PyPI: `strawberry-graphql` — affected >=0 <0.312.3

## Details
Strawberry GraphQL's WebSocket subscription handlers for both the `graphql-transport-ws` and legacy `graphql-ws` protocols allocate an `asyncio.Task` and associated `Operation` object for every incoming subscribe message without enforcing any limit on the number of active subscriptions per connection.

An unauthenticated attacker can open a single WebSocket connection, send connection_init, and then flood subscribe messages with unique IDs. Each message unconditionally spawns a new `asyncio.Task` and async generator, causing linear memory growth and event loop saturation. This leads to server degradation or an OOM crash.

## References
- https://github.com/strawberry-graphql/strawberry/security/advisories/GHSA-hv3w-m4g2-5x77
- https://nvd.nist.gov/vuln/detail/CVE-2026-35526
- https://github.com/strawberry-graphql/strawberry/commit/0977a4e6b41b7cfe3e9d8ba84a43458a2b0c54c2
- https://github.com/pypa/advisory-database/tree/main/vulns/strawberry-graphql/PYSEC-2026-134.yaml
- https://github.com/strawberry-graphql/strawberry
- https://github.com/strawberry-graphql/strawberry/releases/tag/0.312.3
