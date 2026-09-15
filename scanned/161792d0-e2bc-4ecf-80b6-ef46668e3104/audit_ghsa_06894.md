# [M] Hubuum client library (Rust): Configured custom transports may be bypassed, exposing credentials and network traffic

## Summary
Severity: Medium
Advisory: GHSA-qqc3-94qv-7fw3
CWE: CWE-693
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-qqc3-94qv-7fw3
Type: github-advisory

## Affected
- crates.io: `hubuum_client` — affected >=0.3.0 <0.6.1

## Details
## Summary

When an application configures hubuum_client with ClientBuilder::with_transport, several client operations still use the built-in reqwest client directly. The bypass includes password login, bearer-token validation, authentication-provider discovery, health and readiness probes, export-output downloads, and unified-search streams.

## Impact

Applications may use a custom transport as a security boundary for network isolation, proxy enforcement, request signing, audit logging, or policy checks. Affected operations bypass those controls and make direct network requests to the configured base URL. Password login can therefore send plaintext credentials outside the intended transport, while token validation can send a bearer token outside it. Other bypassing calls can evade audit and routing policy.

The issue affects custom transports introduced in 0.3.0. Applications that do not configure a custom transport are not affected by the bypass.

## Defense in depth

The same private fix disables redirect following for built-in async and blocking clients so an authenticated request remains at the endpoint validated and constructed by the client. Applications supplying a preconfigured reqwest client continue to control its redirect policy.

## Remediation

The proposed fix routes authentication, public discovery and probe calls, export downloads, unified-search streams, raw requests, and typed requests through the configured transport in both async and blocking clients. It preserves retry and error-body policies, documents the buffering semantics of custom transports, and surfaces built-in-client redirects as 3xx API errors.

## Validation

Regression tests assert async and blocking routing, paths, login bodies, bearer headers, streaming bodies, retries, error handling, and redirect behavior. Formatting, Clippy with warnings denied, rustdoc warnings, the complete workspace suite, all supported feature combinations, Rust 1.88 MSRV, OpenAPI validation, and the combined library plus downstream-consumer integration suites pass against the immutable Hubuum 0.0.3 image.

## References
- https://github.com/hubuum/hubuum-client-rust/security/advisories/GHSA-qqc3-94qv-7fw3
- https://github.com/hubuum/hubuum-client-rust/commit/5a5c275ffa45f342459b7d3e977926da643bde50
- https://github.com/hubuum/hubuum-client-rust
- https://github.com/hubuum/hubuum-client-rust/releases/tag/v0.6.1
