# [C] @fastify/middie vulnerable to middleware authentication bypass in child plugin scopes

## Summary
Severity: Critical
Advisory: GHSA-72c6-fx6q-fr5w
CVE: CVE-2026-6270
CWE: CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-72c6-fx6q-fr5w
Type: github-advisory

## Affected
- npm: `@fastify/middie` — affected >=0 <9.3.2

## Details
### Impact

`@fastify/middie` v9.3.1 and earlier incorrectly re-prefixes middleware paths when propagating them to child plugin scopes. When a child plugin is registered with a prefix that overlaps with a parent-scoped middleware path, the middleware path is modified during inheritance and silently fails to match incoming requests.

This results in complete bypass of middleware security controls for all routes defined within affected child plugin scopes, including nested (grandchild) scopes. Authentication, authorization, rate limiting, and any other middleware-based security mechanisms are skipped. No special request crafting or configuration is required.

This is the same vulnerability class as [GHSA-hrwm-hgmj-7p9c](https://github.com/fastify/fastify-express/security/advisories/GHSA-hrwm-hgmj-7p9c) (CVE-2026-33807) in `@fastify/express`.

### Patches

Upgrade to `@fastify/middie` v9.3.2 or later.

### Workarounds

None. Upgrade to the patched version.

## References
- https://github.com/fastify/fastify-express/security/advisories/GHSA-hrwm-hgmj-7p9c
- https://github.com/fastify/middie/security/advisories/GHSA-72c6-fx6q-fr5w
- https://nvd.nist.gov/vuln/detail/CVE-2026-6270
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/middie
