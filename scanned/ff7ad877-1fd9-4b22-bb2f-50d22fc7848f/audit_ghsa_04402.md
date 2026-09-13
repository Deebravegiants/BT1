# [H] hono: CORS Middleware reflects any Origin with credentials when `origin` defaults to the wildcard

## Summary
Severity: High
Advisory: GHSA-88fw-hqm2-52qc
CVE: CVE-2026-54290
CWE: CWE-942
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-88fw-hqm2-52qc
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.25

## Details
### Summary

With `credentials: true` and no explicit `origin` (the default wildcard), the CORS Middleware reflects the request's `Origin` and sends `Access-Control-Allow-Credentials: true`. Any site can then make credentialed cross-origin requests and read the responses, exposing cookie-authenticated endpoints to arbitrary origins.

### Details

The spec forbids `Access-Control-Allow-Origin: *` with credentials and browsers reject it, so this configuration used to fail closed. In affected versions the middleware reflects the request `Origin` instead, so it now succeeds for every origin, including `null`. The preflight also echoes the requested headers back, approving non-simple credentialed requests too.

This issue arises when an application enables `credentials: true` and leaves `origin` unset or set to the wildcard.

### Impact

Any third-party page a logged-in user visits can read the application's cookie-authenticated endpoints and perform credentialed state-changing requests. This affects applications that enable credentialed CORS without restricting `origin`.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-88fw-hqm2-52qc
- https://nvd.nist.gov/vuln/detail/CVE-2026-54290
- https://github.com/honojs/hono
