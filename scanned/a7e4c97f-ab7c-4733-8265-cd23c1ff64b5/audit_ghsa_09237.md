# [M] TanStack Start - Server Core: Inbound server-function request deserialization could invoke a sibling client-referenced server function

## Summary
Severity: Medium
Advisory: GHSA-9m65-766c-r333
CWE: CWE-502, CWE-843
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-9m65-766c-r333
Type: github-advisory

## Affected
- npm: `@tanstack/start-server-core` — affected >=0 <1.167.30

## Details
### Summary
A type-confusion bug in seroval ≤ 1.5.2 ([upstream advisory](https://github.com/lxsmnsyc/seroval/security/advisories)) allowed a crafted JSON body sent to one TanStack Start server function to trigger invocation of a different client-referenced server function as a side effect of deserializing the request payload.

This is not an authentication bypass and not remote code execution. The mechanism only invokes server functions that the same client could already reach directly via /_serverFn/<id>, and the target function's full middleware chain — including any user-supplied authentication, authorization, and inputValidator — runs as it would on a direct call.

### Impact
To be exploitable in any meaningful sense, an application would need to expose a client-referenced server function that:

- [ ] Performs a privileged side effect, and
- [ ] Has no authentication/authorization middleware, and
- [ ] Has no input validation

A function meeting all three is already directly callable by any unauthenticated client at its own endpoint, so the practical impact on correctly-written applications is nil. The residual concerns are:

A request to function A could cause function B to also execute, which may surprise observability/audit logging that keys off the request URL.

Request-level middleware (as opposed to per-function middleware) does not re-run for the inner invocation.
Server-only functions (isClientReferenced: false) cannot be reached through this mechanism.

### Patches
Upgrade to @tanstack/start-server-core ≥ 1.167.30 (or the equivalent dated release of @tanstack/react-start / @tanstack/solid-start). The fix bumps seroval to ≥ 1.5.3 and adds defense-in-depth to the serialization adapter plugin shape so adapter payloads cannot be confused with internal seroval node types.

### Workarounds
If you cannot upgrade immediately, ensure every createServerFn(...) exposed to the client has both an .inputValidator(...) and authentication/authorization middleware via .middleware([...]). This is recommended regardless of this advisory.

### Credits
- [Mufeed VH](https://x.com/mufeedvh) of [Winfunc Research](https://winfunc.com/)
- Upstream fix coordinated with Seroval maintainers https://github.com/lxsmnsyc/seroval

## References
- https://github.com/TanStack/router/security/advisories/GHSA-9m65-766c-r333
- https://github.com/TanStack/router
- https://github.com/lxsmnsyc/seroval/security/advisories
