# [H] Nest: Middleware Bypass on Fastify via Trailing Slash

## Summary
Severity: High
Advisory: GHSA-6v32-fjc9-9qf6
CVE: CVE-2026-54281
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-6v32-fjc9-9qf6
Type: github-advisory

## Affected
- npm: `@nestjs/platform-fastify` — affected >=0 <11.1.24

## Details
### Impact

An authentication bypass vulnerability exists in `@nestjs/platform-fastify` (confirmed on version `11.1.24`, the latest available release at time of report). When middleware is registered through NestJS's `MiddlewareConsumer.forRoutes()` API on the Fastify adapter, an unauthenticated client can bypass the Nest middleware registered for that route by simply appending a trailing slash (`/`) to the request URL.

This bypass works on the **default Fastify adapter configuration** — no special router options need to be enabled. Applications using the standard CRUD route shape (`GET /resource` and `GET /resource/:id`) are affected when they protect those routes with `MiddlewareConsumer.forRoutes()` middleware.

### Patches

Fixed in `@nestjs/platform-fastify@11.1.24`

### References

Kudos goes to @a-tt-om

## References
- https://github.com/nestjs/nest/security/advisories/GHSA-6v32-fjc9-9qf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-54281
- https://github.com/nestjs/nest
