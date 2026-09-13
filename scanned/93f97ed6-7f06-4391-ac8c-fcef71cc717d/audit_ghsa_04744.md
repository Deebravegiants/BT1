# [M] Hono: JWT middleware accepts any Authorization scheme, not only Bearer

## Summary
Severity: Medium
Advisory: GHSA-f577-qrjj-4474
CVE: CVE-2026-47673
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-f577-qrjj-4474
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.21

## Details
### Summary

The `jwt` and `jwk` middlewares do not verify that the `Authorization` header value uses the`Bearer` scheme. Any two-part header value — regardless of the scheme name in the first position — proceeds to JWT verification. A request presenting a valid JWT under a non-`Bearer` scheme identifier (such as `Basic` or `Token`) is authenticated identically to a correctly formed `Bearer` request.

### Details

When processing an `Authorization` (or custom) header, the middleware splits the value on whitespace and uses the second token as the JWT to verify. It does not check that the first token is `bearer` (case-insensitively). RFC 6750 specifies that JWT bearer tokens must be presented using the `Bearer` scheme; other scheme identifiers carry distinct semantics and may be subject to different policies in network-layer security controls.

This discrepancy means that scheme-aware external controls — such as WAF rules, API gateways, or reverse proxies that apply policies specific to the `Bearer` scheme identifier — can be bypassed by presenting a valid JWT under a different scheme name.

This issue affects `hono/jwt` and `hono/jwk` middleware.

### Impact

An attacker who possesses a valid JWT may present it under a non-`Bearer` scheme identifier and still pass middleware authentication.

This may lead to:

- Bypass of network-layer security controls that inspect or filter requests based on the authorization scheme identifier
- Token reuse across authentication schemes in applications that use multiple authorization mechanisms

This issue affects applications where `hono/jwt` or `hono/jwk` authentication is combined with external controls that enforce scheme-based access policies.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-f577-qrjj-4474
- https://nvd.nist.gov/vuln/detail/CVE-2026-47673
- https://github.com/honojs/hono/commit/5463db2735476959b8af67756f4e513f4fe19115
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.21
