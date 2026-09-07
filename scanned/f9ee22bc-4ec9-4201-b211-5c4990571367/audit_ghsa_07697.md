# [H] @fastify/middie has Improper Path Normalization when Using Path-Scoped Middleware

## Summary
Severity: High
Advisory: GHSA-8p85-9qpw-fwgw
CVE: CVE-2026-2880
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-28
Source: https://github.com/advisories/GHSA-8p85-9qpw-fwgw
Type: github-advisory

## Affected
- npm: `@fastify/middie` — affected >=0 <9.2.0

## Details
## Summary
A path normalization inconsistency in `@fastify/middie` can result in authentication/authorization bypass when using path-scoped middleware (for example, `app.use('/secret', auth)`).

When Fastify router normalization options are enabled (such as `ignoreDuplicateSlashes`, `useSemicolonDelimiter`, and related trailing-slash behavior), crafted request paths may bypass middleware checks while still being routed to protected handlers.

## Impact
An unauthenticated remote attacker can access endpoints intended to be protected by middleware-based auth/authorization controls by sending specially crafted URL paths (for example, `//secret` or `/secret;foo=bar`), depending on router option configuration.

This may lead to unauthorized access to protected functionality and data exposure.

## Affected versions
- Confirmed affected: `@fastify/middie@9.1.0`
- All versions prior to the patch are affected.

## Patched versions
- Fixed in: *9.2.0*

## Details
The issue is caused by canonicalization drift between:
1. `@fastify/middie` path matching for `app.use('/prefix', ...)`, and
2. Fastify/find-my-way route lookup normalization.

Because middleware and router did not always evaluate the same normalized path, auth middleware could be skipped while route resolution still succeeded.

## Workarounds
Until patched version is deployed:
- Avoid relying solely on path-scoped middie guards for auth/authorization.
- Enforce auth at route-level handlers/hooks after router normalization.
- Disable risky normalization combinations only if operationally feasible.

## Resources
- Fluid Attacks Disclosure Policy: https://fluidattacks.com/advisories/policy
- Fluid Attacks advisory URL: https://fluidattacks.com/advisories/jimenez

## Credits
- **Cristian Vargas** (Fluid Attacks Research Team) — discovery and report.
- **Oscar Uribe** (Fluid Attacks) — coordination and disclosure.

## References
- https://github.com/fastify/middie/security/advisories/GHSA-8p85-9qpw-fwgw
- https://nvd.nist.gov/vuln/detail/CVE-2026-2880
- https://github.com/fastify/middie/commit/140e0dd0359d890fec7e6ea1dcc5134d6bd554d4
- https://fluidattacks.com/advisories/jimenez
- https://fluidattacks.com/advisories/policy
- https://github.com/fastify/middie
- https://github.com/fastify/middie/releases/tag/v9.2.0
