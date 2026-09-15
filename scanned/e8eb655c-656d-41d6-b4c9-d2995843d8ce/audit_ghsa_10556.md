# [H] Directus: Unauthenticated Denial of Service via GraphQL Alias Amplification of Expensive Health Check Resolver

## Summary
Severity: High
Advisory: GHSA-6q22-g298-grjh
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-6q22-g298-grjh
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.17.0

## Details
## Summary

The GraphQL specification permits a single query to repeat the same field multiple times using aliases, with each alias resolved independently by default. Directus did not deduplicate resolver invocations within a single request, meaning each alias triggered a full, independent execution of the underlying resolver.

The health check resolver ran all backend checks (database connectivity, cache, storage writes, and SMTP verification) on every invocation. Combined with unauthenticated access to the system GraphQL endpoint, this allowed an attacker to amplify resource consumption significantly from a single HTTP request, exhausting the database connection pool, storage I/O, and SMTP connections.

## Fix

A request-scoped resolver deduplication mechanism was introduced and applied broadly across all GraphQL read resolvers, both system and items endpoints. When multiple aliases in a single request invoke the same resolver with identical arguments, only the first call executes; all subsequent aliases share its result. This eliminates the amplification factor regardless of how many aliases an attacker includes in a query.

## Impact

- **Service degradation or outage:** Database connection pool exhaustion prevents all Directus operations for all users
- **Storage I/O saturation:** Concurrent file writes can overwhelm disk I/O
- **SMTP resource exhaustion:** Concurrent SMTP verification calls may overwhelm the mail server
- **No authentication required:** Any network-accessible attacker can trigger this condition
- **Single-request impact:** A single request is sufficient to cause significant resource consumption

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/directus/directus/security/advisories/GHSA-6q22-g298-grjh
- https://github.com/directus/directus
