# [M] OpenID Connect nonce generated but never validated — ID token replay attack

## Summary
Severity: Medium
Advisory: GHSA-3gx8-q682-38mx
CVE: CVE-2026-42206
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-3gx8-q682-38mx
Type: github-advisory

## Affected
- Packagist: `roadiz/openid` — affected >=2.7.0 <2.7.18
- Packagist: `roadiz/openid` — affected >=2.6.0 <2.6.31
- Packagist: `roadiz/openid` — affected >=2.5.0 <2.5.45
- Packagist: `roadiz/openid` — affected >=0 <2.3.43

## Details
### Summary
The `roadiz/openid` package generates an OIDC nonce in `OAuth2LinkGenerator::generate()` and includes it in the authorization request sent to the identity provider, but **never stores it** and **never validates it** on the callback. The `OpenIdJwtConfigurationFactory` validation chain does not include a nonce constraint, and `OpenIdAuthenticator::authenticate()` never checks the nonce claim in the returned ID token against a stored value.

### Details
In `src/OAuth2LinkGenerator.php`, a nonce is created and sent to the IdP:
```php
'nonce' => $this->tokenGenerator->generateToken(),
```
However, this value is neither stored in session, cache, nor any other persistent store.

In `src/OpenIdJwtConfigurationFactory.php`, the JWT validation constraints are:
- `LooseValidAt` (expiry)
- `PermittedFor` (audience)
- `IssuedBy` (issuer)
- `HostedDomain` (optional)
- `UserInfoEndpoint` (optional)

**No nonce constraint is present.**

In `src/Authentication/OpenIdAuthenticator.php`, the `authenticate()` method validates the state CSRF token correctly (fixed in v2.7.10), but never retrieves a stored nonce or compares it against the `nonce` claim in the ID token.

### PoC
1. Obtain a valid ID token from a legitimate OIDC flow for a target user (e.g. via network interception, browser history leak, or referrer header exposure on a non-HTTPS redirect).
2. Replay the ID token: Since the nonce in the token is never cross-checked against a client-stored value, the token passes all validation constraints as long as it has not expired.
3. Result: An attacker can authenticate as the victim within the ID token's validity window.

Additionally, in an authorization code flow with multiple concurrent sessions, a malicious IdP or a compromised token endpoint could inject a token with a mismatched nonce, and the application would accept it silently.

### Impact
- **ID token replay attacks**: Valid but intercepted tokens can be reused for authentication within their validity period.
- **Token injection attacks**: A malicious or compromised identity provider can inject tokens across sessions without detection.
- Affects any Roadiz application using the `roadiz/openid` package with OpenID Connect SSO.

The OIDC Core 1.0 specification (Section 3.1.3.7) explicitly requires clients to verify the `nonce` claim if it was present in the authorization request.

## References
- https://github.com/roadiz/core-bundle-dev-app/security/advisories/GHSA-3gx8-q682-38mx
- https://nvd.nist.gov/vuln/detail/CVE-2026-42206
- https://github.com/roadiz/core-bundle-dev-app
