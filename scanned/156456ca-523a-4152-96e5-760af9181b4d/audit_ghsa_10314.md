# [M] Directus: GraphQL Alias Amplification Denial of Service Due to Missing Query Cost/Complexity Limits

## Summary
Severity: Medium
Advisory: GHSA-ph52-67fq-75wj
CVE: CVE-2026-35441
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-ph52-67fq-75wj
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.17.0

## Details
### Summary

Directus' GraphQL endpoints (`/graphql` and `/graphql/system`) did not deduplicate resolver invocations within a single request. An authenticated user could exploit GraphQL aliasing to repeat an expensive relational query many times in a single request, forcing the server to execute a large number of independent complex database queries concurrently, multiplying database load linearly with the number of aliases. The existing token limit on GraphQL queries still permitted enough aliases for significant resource exhaustion, while the relational depth limit applied per alias without reducing the total number executed. Rate limiting is disabled by default, meaning no built-in throttle prevented this from causing CPU, memory, and I/O exhaustion that could degrade or crash the service. Any authenticated user, including those with minimal read-only permissions, could trigger this condition.

### Fix

A request-scoped resolver deduplication mechanism was introduced and applied broadly across all GraphQL read resolvers, both system and items endpoints. When multiple aliases in a single request invoke the same resolver with identical arguments, only the first call executes; all subsequent aliases share its result. This eliminates the amplification factor regardless of how many aliases a query contains.

### Impact

- **Service degradation or outage:** Concurrent complex database queries exhaust the connection pool and server resources, affecting all users
- **Low privilege required:** Any authenticated user, including those with read-only access to a single collection, can trigger this condition
- **Linear scaling:** Impact scales with the number of aliases and depth of relational queries
- **Compounded by concurrency:** Multiple simultaneous requests multiply the effect further

## References
- https://github.com/directus/directus/security/advisories/GHSA-ph52-67fq-75wj
- https://nvd.nist.gov/vuln/detail/CVE-2026-35441
- https://github.com/directus/directus
