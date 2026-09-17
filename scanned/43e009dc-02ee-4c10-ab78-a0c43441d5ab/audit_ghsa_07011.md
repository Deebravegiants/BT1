# [M] Hubuum client library (Rust): Authenticated requests may escape the configured base path through redirects

## Summary
Severity: Medium
Advisory: GHSA-f45q-w629-wr25
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-f45q-w629-wr25
Type: github-advisory

## Affected
- crates.io: `hubuum_client` — affected >=0.0.1 <0.6.1

## Details
## Impact

The built-in async and blocking clients used reqwest's default redirect policy. `BaseUrl` constrains the initial request to the configured origin and path prefix, but redirect processing occurs after that validation. reqwest retains sensitive headers when a redirect changes only the path on the same scheme, host, and port. A redirect from a Hubuum endpoint to another path on a shared origin could therefore carry the bearer `Authorization` header outside the configured Hubuum path prefix.

Exploitation requires an attacker, compromised server, or intermediary to influence a 3xx response. Cross-origin redirects are not affected because reqwest strips sensitive headers when scheme, host, or port changes.

## Patches

Version 0.6.1 configures both built-in HTTP clients with `reqwest::redirect::Policy::none()`. Redirect responses are returned as 3xx API errors instead of being followed. Supplying a preconfigured reqwest client remains an explicit opt-in to that client's redirect policy.

## Workarounds

On affected versions, construct a reqwest client with `reqwest::redirect::Policy::none()` and pass it through `with_http_client`. Deployments can also reduce exposure by ensuring the Hubuum origin is not shared with other applications and that trusted infrastructure never redirects API requests outside the configured path prefix.

## References
- https://github.com/hubuum/hubuum-client-rust/security/advisories/GHSA-f45q-w629-wr25
- https://github.com/hubuum/hubuum-client-rust/commit/5a5c275ffa45f342459b7d3e977926da643bde50
- https://github.com/hubuum/hubuum-client-rust
