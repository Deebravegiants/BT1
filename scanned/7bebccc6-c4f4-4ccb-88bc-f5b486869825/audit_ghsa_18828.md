# [H] Hono Improper Authorization vulnerability

## Summary
Severity: High
Advisory: GHSA-m732-5p4w-x69g
CVE: CVE-2025-62610
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-m732-5p4w-x69g
Type: github-advisory

## Affected
- npm: `hono` — affected >=1.1.0 <4.10.2

## Details
### Improper Authorization in Hono (JWT Audience Validation)

Hono’s JWT authentication middleware did not validate the `aud` (Audience) claim by default. As a result, applications using the middleware without an explicit audience check could accept tokens intended for other audiences, leading to potential cross-service access (token mix-up).

The issue is addressed by adding a new `verification.aud` configuration option to allow RFC 7519–compliant audience validation. This change is classified as a **security hardening improvement**, but the lack of validation can still be considered a vulnerability in deployments that rely on default JWT verification.

### Recommended secure configuration

You can enable RFC 7519–compliant audience validation using the new `verification.aud` option:

```ts
import { Hono } from 'hono'
import { jwt } from 'hono/jwt'

const app = new Hono()

app.use(
  '/api/*',
  jwt({
    secret: 'my-secret',
    verification: {
      // Require this API to only accept tokens with aud = 'service-a'
      aud: 'service-a',
    },
  })
)
```

Below is the original description by the reporter. For security reasons, it does not include PoC reproduction steps, as the vulnerability can be clearly understood from the technical description.

---

## The original description by the reporter

### Summary
Hono’s **JWT Auth Middleware does not provide a built-in `aud` (Audience) verification option**, which can cause **confused-deputy / token-mix-up** issues: an API may accept a valid token that was **issued for a different audience** (e.g., another service) when multiple services share the same issuer/keys. This can lead to unintended cross-service access. Hono’s docs list verification options for `iss/nbf/iat/exp` only, with **no `aud` support**; RFC 7519 requires that when an `aud` claim is present, tokens **MUST** be rejected unless the processing party identifies itself in that claim.

**Note:** This problem likely exists in the **JWK/JWKS-based middleware** as well (e.g., `jwk` / `verifyWithJwks`)

### Details
- The middleware’s `verifyOptions` enumerate only `iss`, `nbf`, `iat`, and `exp`; there is **no `aud` option**. The same omission appears in the JWT Helper’s “Payload Validation” list. Developers relying on the middleware for complete standards-aligned validation therefore won’t check audience by default.
- **Standards requirement:** RFC 7519 §4.1.3 states that each principal intended to process the JWT **MUST** identify itself with a value in the `aud` claim; if it does not, the JWT **MUST** be rejected (when `aud` is present). Lack of a first-class `aud` check increases the risk that tokens issued for **Service B** are accepted by **Service A**.
- **Real-world effect:** In deployments with a single IdP/JWKS and shared keys across multiple services, a token minted for one audience can be mistakenly accepted by another audience unless developers implement a custom audience check.
    - For example, with Google Identity (OIDC), iss is always https://accounts.google.com (shared across apps), but aud differs per application because it is that app’s OAuth client ID; therefore, an attacker can host a separate service that supports “Sign in with Google,” obtain a valid ID token (JWT) for the victim user, and—if your API does not verify aud—use that token to access your API with the victim’s privileges.

### Impact
**Type:** Authentication/authorization weakness via **token mix-up (confused-deputy)**.

**Who is impacted:** Any Hono user who:
- shares an issuer/keys across multiple services (common with a single IdP/JWKS)
- distinguishes tokens by intended recipient using `aud`.

**What can happen:**
- **Cross-service access:** A token for *Service B* may be accepted by *Service A*.
- **Boundary erosion:** ID tokens and access tokens, or separate API audiences, can be inadvertently intermixed.
    - This may causes unauthorized invocation of sensitive endpoints.

**Recommended remediation:**
1) Add `verifyOptions.aud` (`string | string[] | RegExp`) to the middleware and enforce RFC 7519 semantics: In [verify method](https://github.com/honojs/hono/blob/db764c2f1d8a2905d66c78c41aa47e47d3a4165d/src/utils/jwt/jwt.ts#L99-L156), if `aud` is present and does not match with specified audiences, reject.
2) Ensure equivalent `aud` handling exists in the JWK/JWKS flow (`jwk` middleware / `verifyWithJwks`) so users of external IdPs can enforce audience consistently.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-m732-5p4w-x69g
- https://nvd.nist.gov/vuln/detail/CVE-2025-62610
- https://github.com/honojs/hono/commit/45ba3bf9e3dff8e4bd85d6b47d4b71c8d6c66bef
- https://github.com/honojs/hono
