# [H] gRPC-Go xDS servers: Denial of Service (DoS) via crash due to missing `:authority` and `Host` headers

## Summary
Severity: High
Advisory: GHSA-2v4p-qf9q-27wj
Aliases: CVE-2026-84445
Ecosystem: Go
Published: 2026-09-08
Source: https://osv.dev/vulnerability/GHSA-2v4p-qf9q-27wj
Type: osv

## Affected
- Go: `google.golang.org/grpc` — affected >=0 <1.82.2
- Go: `google.golang.org/grpc` — affected >=1.83.0 <1.83.2
- Go: `google.golang.org/grpc` — affected >=1.84.0-dev <1.85.0-dev.0.20260825072537-93e31b48545e

## Details
A vulnerability exists in gRPC-Go servers configured with `xds.NewGRPCServer()` where a crafted request missing both `:authority` and `Host` headers can cause a server panic, resulting in a Denial of Service (DoS).

Servers built with `xds.NewGRPCServer` install an xDS routing interceptor on every RPC. This interceptor looks up the request’s `:authority` header to pick a virtual host. The HTTP/2 server transport previously accepted requests that had neither `:authority` nor `Host`. When this happened, the xDS routing interceptor attempted to access the first element of an empty slice of authorities, leading to an index out of bounds panic. Since the per-RPC goroutine does not recover from panics, the entire server process would terminate.

This panic occurs in the interceptor pipeline, meaning the transport credentials handshake (TLS, mTLS, or ALTS) and HTTP/2 connection establishment must complete successfully before the crafted request can reach this logic.
- Insecure/Standard TLS: If the server permits insecure (plaintext) connections or standard credentials (where client certs are not checked), any unauthenticated remote attacker can trigger the crash.
- mTLS / ALTS: If strict transport-level authentication is enforced at the network edge or transport layer (e.g., requiring a valid client certificate), the attacker must possess valid transport credentials to initiate the stream and trigger the panic.

### Impact
An attacker can cause a complete outage of the gRPC server by sending a request missing both `:authority` and `Host` headers, provided they can successfully establish a transport connection.

### Patches
The issue has been addressed in `master` (and backported to `1.83.2` and `1.82.2`). The fix updates the HTTP/2 transport layer to reject requests missing both `:authority` and `Host` headers early, maintaining consistency with and other gRPC language implementations.

## References
- https://github.com/grpc/grpc-go/security/advisories/GHSA-2v4p-qf9q-27wj
- https://github.com/grpc/grpc-go/issues/9354
- https://github.com/grpc/grpc-go/pull/9365
- https://github.com/grpc/grpc-go/pull/9366
- https://github.com/grpc/grpc-go/pull/9367
- https://github.com/grpc/grpc-go/commit/3822494d8ea03b992c089fd2a195f041762fffb7
- https://github.com/grpc/grpc-go/commit/8668b69c167df908b6b3666dcbf40992b9e932a4
- https://github.com/grpc/grpc-go/commit/93e31b48545e2a8aaeb6e06b47fb249f94e6297f
- https://github.com/grpc/grpc-go
- https://github.com/grpc/grpc-go/releases/tag/v1.82.2
- https://github.com/grpc/grpc-go/releases/tag/v1.83.2
