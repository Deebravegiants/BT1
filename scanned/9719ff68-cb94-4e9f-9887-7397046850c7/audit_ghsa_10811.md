# [M] Parse Server's GraphQL WebSocket endpoint bypasses security middleware

## Summary
Severity: Medium
Advisory: GHSA-p2x3-8689-cwpg
CVE: CVE-2026-32594
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-p2x3-8689-cwpg
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.14
- npm: `parse-server` — affected >=0 <8.6.40

## Details
### Impact

Any Parse Server deployment that uses the GraphQL API is affected. The GraphQL WebSocket endpoint for subscriptions does not pass requests through the Express middleware chain that enforces authentication, introspection control, and query complexity limits. An attacker can connect to the WebSocket endpoint and execute GraphQL operations without providing a valid application or API key, access the GraphQL schema via introspection even when public introspection is disabled, and send arbitrarily complex queries that bypass configured complexity limits.

### Patches

The unfinished GraphQL WebSocket subscription feature has been removed, including the `createSubscriptions` method and the `subscriptions-transport-ws` dependency. GraphQL subscriptions were never functional in Parse Server as the schema did not define any subscription types.

### Workarounds

Block WebSocket upgrade requests to the GraphQL subscriptions path (by default `/subscriptions`) at the network level, for example using a reverse proxy or load balancer rule.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-p2x3-8689-cwpg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32594
- https://github.com/parse-community/parse-server/pull/10189
- https://github.com/parse-community/parse-server/pull/10190
- https://github.com/parse-community/parse-server/commit/21330d146c68b57a930a58b8a8cd9fbf09436cf3
- https://github.com/parse-community/parse-server/commit/3ffba757bfc836bd034e1369f4f64304e110e375
- https://github.com/parse-community/parse-server
