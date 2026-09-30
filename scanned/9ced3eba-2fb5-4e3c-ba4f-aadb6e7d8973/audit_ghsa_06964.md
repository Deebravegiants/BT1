# [M] @asymmetric-effort/specifyjs: GraphQL gql tag allows metacharacter injection

## Summary
Severity: Medium
Advisory: GHSA-5c7w-4wm3-85vw
CWE: CWE-943
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-5c7w-4wm3-85vw
Type: github-advisory

## Affected
- npm: `@asymmetric-effort/specifyjs` — affected >=0 <0.2.136

## Details
## Finding

**Location**: `core/src/client/graphql.ts:66-80`

The `gql` template tag function warned about interpolated values containing GraphQL metacharacters (`{}():`) but still concatenated them into the query string, enabling potential GraphQL injection.

## Status

**Fixed in v0.2.136** — The `gql` function now throws an error when metacharacters are detected in interpolated values, forcing developers to use the `variables` parameter.

## References
- https://github.com/asymmetric-effort/specifyjs/security/advisories/GHSA-5c7w-4wm3-85vw
- https://github.com/asymmetric-effort/specifyjs/commit/25d1fb491d99479efdf501f5f75e0bb80c908f0a
- https://github.com/asymmetric-effort/specifyjs
