# [H] Nest Fastify HEAD Request Middleware Bypass

## Summary
Severity: High
Advisory: GHSA-wf42-42fg-fg84
CVE: CVE-2026-33011
CWE: CWE-670
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-wf42-42fg-fg84
Type: github-advisory

## Affected
- npm: `@nestjs/platform-fastify` — affected >=0 <11.1.16

## Details
### Impact

In a NestJS application using `@nestjs/platform-fastify`, GET middleware can be bypassed because Fastify automatically redirects HEAD requests to the corresponding GET handlers (if they exist).

As a result:

- Middleware will be completely skipped.
- The HTTP response won't include a body (since the response is truncated when redirecting a HEAD request to a GET handler).
- The actual handler will still be executed.

### Patches

Fixed in `@nestjs/platform-fastify@11.1.16`

## References
- https://github.com/nestjs/nest/security/advisories/GHSA-wf42-42fg-fg84
- https://nvd.nist.gov/vuln/detail/CVE-2026-33011
- https://github.com/nestjs/nest/commit/cbdf737cd6e7cefa52d05ecea2ae4af95c464614
- https://github.com/nestjs/nest
- https://github.com/nestjs/nest/releases/tag/v11.1.17
