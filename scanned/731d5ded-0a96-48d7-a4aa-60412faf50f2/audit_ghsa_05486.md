# [H] Hono JWT Middleware's JWT Algorithm Confusion via Unsafe Default (HS256) Allows Token Forgery and Auth Bypass

## Summary
Severity: High
Advisory: GHSA-f67f-6cw9-8mq4
CVE: CVE-2026-22817
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-f67f-6cw9-8mq4
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.11.4

## Details
## Summary

A flaw in Hono’s JWK/JWKS JWT verification middleware allowed the JWT header’s `alg` value to influence signature verification when the selected JWK did not explicitly specify an algorithm. This could enable **JWT algorithm confusion** and, in certain configurations, allow forged tokens to be accepted.

## Details

When verifying JWTs using JWKs or a JWKS endpoint, the middleware selected the verification algorithm based on the JWK’s `alg` field if present, but otherwise fell back to the `alg` value provided in the unverified JWT header.

Because the `alg` field in a JWK is optional and often omitted in real-world JWKS configurations, this behavior could allow an attacker to control the algorithm used for verification. In some environments, this may lead to authentication or authorization
bypass through crafted tokens.

The practical impact depends on application configuration, including which algorithms are accepted and how JWTs are used for authorization decisions.

## Impact

In affected configurations, an attacker may be able to forge JWTs with attacker-controlled claims, potentially resulting in authentication or authorization bypass.

Applications that do not use the JWK/JWKS middleware, do not rely on JWT-based authentication, or explicitly restrict allowed algorithms are not affected.

## Resolution

Update to the latest patched release.

**Breaking change:**

As part of this fix, the JWT middleware now requires the `alg` option to be explicitly specified. This prevents algorithm confusion by ensuring that the verification algorithm is not derived from untrusted JWT header values.

Applications upgrading must update their configuration accordingly.

### Before (vulnerable configuration)

```ts
import { jwt } from 'hono/jwt'

app.use(
  '/auth/*',
  jwt({
    secret: 'it-is-very-secret',
    // alg was optional
  })
)
```

### After (patched configuration)

```ts
import { jwt } from 'hono/jwt'

app.use(
  '/auth/*',
  jwt({
    secret: 'it-is-very-secret',
    alg: 'HS256', // required
  })
)
```

## References
- https://github.com/honojs/hono/security/advisories/GHSA-f67f-6cw9-8mq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-22817
- https://github.com/honojs/hono/commit/cc0aa7ae327ed84cc391d29086dec2a3e44e7a1f
- https://github.com/honojs/hono
