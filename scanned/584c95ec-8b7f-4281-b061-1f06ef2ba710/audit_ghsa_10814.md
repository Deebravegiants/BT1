# [M] Webauthn Framework: allowed_origins collapses URL-like origins to host-only values, bypassing exact origin validation

## Summary
Severity: Medium
Advisory: GHSA-f7pm-6hr8-7ggm
CVE: CVE-2026-30964
CWE: CWE-346
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-f7pm-6hr8-7ggm
Type: github-advisory

## Affected
- Packagist: `web-auth/webauthn-framework` — affected >=5.2.0 <5.2.4
- Packagist: `web-auth/webauthn-lib` — affected >=5.2.0 <5.2.4
- Packagist: `web-auth/webauthn-symfony-bundle` — affected >=5.2.0 <5.2.4

## Details
### Summary
When `allowed_origins` is configured, `CheckAllowedOrigins` reduces URL-like values to their `host` component and accepts on host match alone. This makes exact origin policies impossible to express: scheme and port differences are silently ignored.

### Details
`CheckAllowedOrigins` stores each configured allowed origin as:

```php
parse_url($allowedOrigin)['host'] ?? $allowedOrigin
```

and later reduces the received `clientDataJSON.origin` the same way:

```php
parse_url($C->origin)['host'] ?? $C->origin
```

If the reduced value matches, the method returns early. As a result, for the normal `allowed_origins` path, the later HTTPS check is not reached.

This differs from [WebAuthn Level 2](https://www.w3.org/TR/webauthn-2/), which requires verifying that `C.origin` matches the RP's origin (scheme + host + port), separately from verifying that `authData.rpIdHash` matches the expected RP ID.

**Affected code:**
- [CheckAllowedOrigins.php](https://github.com/web-auth/webauthn-framework/blob/d58906e/src/webauthn/src/CeremonyStep/CheckAllowedOrigins.php)

**Spec references:**
- [§7.1 Registering a New Credential](https://www.w3.org/TR/webauthn-2/#sctn-registering-a-new-credential)
- [§7.2 Verifying an Authentication Assertion](https://www.w3.org/TR/webauthn-2/#sctn-verifying-assertion)
- [CollectedClientData.origin](https://www.w3.org/TR/webauthn-2/#dom-collectedclientdata-origin)

### PoC
Configuration:

```yaml
webauthn:
  allowed_origins:
    - https://login.example.com:8443
  allow_subdomains: false
```

Send a registration or authentication response whose `clientDataJSON.origin` is:

```text
https://login.example.com:9443
```

**Observed:** the response is accepted, because both values are reduced to `login.example.com`.

**Expected:** the response should be rejected, because `https://login.example.com:8443` and `https://login.example.com:9443` are different origins.

### Impact
This is an origin validation error (CWE-346) affecting deployments that use `allowed_origins`. The most practical browser-facing scenario is same-host / different-port origin confusion. In non-browser or custom clients, scheme confusion may also be relevant.

### Fix
Fixed in version **5.2.4** by rewriting `CheckAllowedOrigins` to perform full origin comparison (scheme + host + port) as required by the WebAuthn spec:

- Origins configured with a scheme (e.g. `https://example.com:8443`) are now stored and compared as full `scheme://host[:port]` values, with default port normalization (443 for HTTPS, 80 for HTTP).
- Origins configured without a scheme are still matched by host only, for backward compatibility.
- Subdomain matching now also verifies scheme and port consistency.

See commit [b4cd9a43](https://github.com/web-auth/webauthn-framework/commit/b4cd9a43).

### Mitigation
Upgrade to `web-auth/webauthn-framework` (or `web-auth/webauthn-lib` / `web-auth/webauthn-symfony-bundle`) **>= 5.2.4**.

## References
- https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-f7pm-6hr8-7ggm
- https://nvd.nist.gov/vuln/detail/CVE-2026-30964
- https://github.com/web-auth/webauthn-framework/commit/535cc3c2dcbd9c3dfd5e00a254ad4a984e5e7839
- https://github.com/web-auth/webauthn-framework/commit/b4cd9a4394c35fcac6080fd2f84f4f58a30abc01
- https://github.com/web-auth/webauthn-framework
