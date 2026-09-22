# [H] Envoy: grpc_stats filter segfault on Connect protocol requests to direct_response routes

## Summary
Severity: High
Advisory: BIT-envoy-2026-47204
Aliases: CVE-2026-47204, GHSA-3jxh-8p6x-7pf6
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-envoy-2026-47204
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. From 1.26.0 until 1.35.13, 1.36.9, 1.37.5, and 1.38.3, the envoy.filters.http.grpc_stats filter crashes (null pointer dereference / segfault) when a Connect protocol request (Content-Type: application/connect+proto or application/connect+json) hits a direct_response route. A single unauthenticated HTTP request crashes the Envoy process. This vulnerability is fixed in 1.35.13, 1.36.9, 1.37.5, and 1.38.3.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-3jxh-8p6x-7pf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-47204
