# [H] Nest has a Fastify URL Encoding Middleware Bypass 

## Summary
Severity: High
Advisory: GHSA-r4wm-x892-vjmx
CVE: CVE-2026-2293
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-r4wm-x892-vjmx
Type: github-advisory

## Affected
- npm: `@nestjs/platform-fastify` — affected >=0 <11.1.14

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

A NestJS application using `@nestjs/platform-fastify` can allow bypass of any middleware when Fastify path-normalization options (e.g., `ignoreTrailingSlash`, `ignoreDuplicateSlashes`, `useSemicolonDelimiter`) are enabled. In affected route-scoped middleware setups, variant paths may skip middleware checks while still reaching the protected handler.

The bug is a path canonicalization mismatch between middleware matching and route matching in Nest’s Fastify adapter.

Nest passes Fastify routerOptions (such as `ignoreTrailingSlash`, `ignoreDuplicateSlashes`, `useSemicolonDelimiter`) to the Fastify router in packages/platform-fastify/adapters/fastify-adapter.ts:253.

But middleware execution is decided by a separate regex check over `req.originalUrl` in packages/platform-fastify/adapters/fastify-adapter.ts:706 and packages/platform-fastify/adapters/fastify-adapter.ts:713.

If that regex does not match, Nest does `next()` and skips the middleware (packages/platform-fastify/adapters/fastify-adapter.ts:714), while Fastify may still normalize the same path and route it to the protected handler. So the vulnerability exists because security checks (middleware) and request dispatch(router) use different URL interpretations.

This is a fail-open design issue (inconsistent normalization), not just a bad app config: non-default router options make the mismatch reachable.

### Patches

Fixed in `@nestjs/platform-fastify@11.1.14`

### References

Credit goes to Fluidattacks ([Cristian Vargas](https://www.linkedin.com/in/cvmiracle/)) https://fluidattacks.com/advisories/neton

## References
- https://github.com/nestjs/nest/security/advisories/GHSA-r4wm-x892-vjmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-2293
- https://github.com/nestjs/nest/commit/fd8d073e0e048b185147209338ca7042e52c10ba
- https://fluidattacks.com/advisories/neton
- https://github.com/nestjs/nest
- https://github.com/nestjs/nest/releases/tag/v11.1.14
