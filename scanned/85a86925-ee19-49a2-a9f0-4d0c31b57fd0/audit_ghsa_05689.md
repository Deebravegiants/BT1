# [H] Hono JWK Auth Middleware has JWT algorithm confusion when JWK lacks "alg" (untrusted header.alg fallback)

## Summary
Severity: High
Advisory: GHSA-3vhc-576x-3qv4
CVE: CVE-2026-22818
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-3vhc-576x-3qv4
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.11.4

## Details
## Summary

A flaw in Hono’s JWK/JWKS JWT verification middleware allowed the algorithm specified in the JWT header to influence signature verification when the selected JWK did not explicitly define an algorithm. This could enable JWT algorithm confusion and, in certain configurations, allow forged tokens to be accepted.

## Details

When verifying JWTs using JWKs or a JWKS endpoint, the middleware selected the verification algorithm based on the JWK’s `alg` field if present. If the JWK did not specify an algorithm, the middleware fell back to using the `alg` value provided in the unverified JWT header.

Because the `alg` field in a JWK is optional and commonly omitted in real-world JWKS configurations, this behavior could allow an attacker to influence which algorithm is used for verification. In some environments, this may result in authentication or authorization bypass through crafted JWTs.

The practical impact depends on application configuration, including which algorithms are accepted and how JWTs are used to make authorization decisions.

## Impact

In affected configurations, an attacker may be able to forge JWTs with attacker-controlled claims, potentially leading to authentication or authorization bypass.

Applications that do not use the JWK/JWKS middleware, do not rely on JWT-based authentication, or explicitly restrict allowed algorithms are not affected.

## Resolution

Update to the latest patched release.

**Breaking change:**

The JWK/JWKS JWT verification middleware has been updated to require an explicit allowlist of asymmetric algorithms when verifying tokens. The middleware no longer derives the verification algorithm from untrusted JWT header values.

Instead, callers must explicitly specify which asymmetric algorithms are permitted, and only tokens signed with those algorithms will be accepted. This prevents JWT algorithm confusion by ensuring that algorithm selection is fully controlled by application
configuration.

As part of this fix, the `alg` option is now required when using the JWK/JWKS middleware, and symmetric (HS*) algorithms are no longer accepted in this context.

### Before (vulnerable configuration)

```ts
import { jwk } from 'hono/jwk'

app.use(
  '/auth/*',
  jwk({
    jwks_uri: 'https://example.com/.well-known/jwks.json',
    // alg was optional
  })
)
```

### After (patched configuration)

```ts
import { jwk } from 'hono/jwk'

app.use(
  '/auth/*',
  jwk({
    jwks_uri: 'https://example.com/.well-known/jwks.json',
    alg: ['RS256'], // required: explicit asymmetric algorithm allowlist
  })
)
```

## References
- https://github.com/honojs/hono/security/advisories/GHSA-3vhc-576x-3qv4
- https://nvd.nist.gov/vuln/detail/CVE-2026-22818
- https://github.com/honojs/hono/commit/190f6e28e2ca85ce3d1f2f54db1310f5f3eab134
- https://github.com/honojs/hono
