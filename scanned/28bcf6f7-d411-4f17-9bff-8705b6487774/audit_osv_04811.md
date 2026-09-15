# [M] Envoy: ext_authz Use-After-Free during Stream Teardown with Per-Route Overrides

## Summary
Severity: Medium
Advisory: BIT-envoy-2026-47205
Aliases: CVE-2026-47205, GHSA-mvh9-767w-x47j
Ecosystem: Bitnami
Published: 2026-06-30
Source: https://osv.dev/vulnerability/BIT-envoy-2026-47205
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. From 1.36.0 until 1.36.9, 1.37.5, and 1.38.3, a Use-After-Free (UAF) vulnerability leading to a sudden segmentation fault exists in Envoy's ext_authz HTTP filter when processing per-route authorization overrides concurrently with rapid downstream client disconnects. During standard request lifecycles, Envoy instantiates the ext_authz filter with a foundational authorization client object (client_). If a matched route dictates a dynamic per-route HTTP or gRPC authorization service override, the filter generates a localized client. In the vulnerable implementation, this transient client aggressively overwrote the default client_ unique pointer by executing client_ = std::move(per_route_client). When a client rapidly establishes and subsequently tears down a stream (such as rapidly refreshing a protected WebSocket endpoint), the downstream triggers the ConnectionManagerImpl::doDeferredStreamDestroy() -> ActiveStream::onResetStream() lifecycle. Envoy immediately sequences Filter::onDestroy() in an attempt to securely abort dispatched asynchronous authorization check transactions via client_->cancel(). By destructing the default client abruptly during initiateCall, a memory lifecycle misalignment occurs within the async client manager. The stream teardown fails to reliably track and cancel the dynamically bound asynchronous authorization tasks, orchestrating a sequence where a late asynchronous callback from the network evaluates against a heavily destroyed ActiveStream validation span, generating a UAF process crash. This vulnerability is fixed in 1.36.9, 1.37.5, and 1.38.3.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-mvh9-767w-x47j
- https://nvd.nist.gov/vuln/detail/CVE-2026-47205
