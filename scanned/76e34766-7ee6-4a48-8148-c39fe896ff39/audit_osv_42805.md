# [C] Centrifugo: Client-forgeable headers emulation lets any client spoof headers forwarded to proxy backends

## Summary
Severity: Critical
Advisory: CVE-2026-71485
Aliases: GHSA-9468-v6mj-fppw
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-71485
Type: osv

## Details
Centrifugo is an open-source scalable real-time messaging server. Prior to 6.9.0, Centrifugo copies the client-controlled protocol.ConnectRequest.headers map through OnClientConnecting in internal/client/handler.go, ConnectEvent.Headers, and SetEmulatedHeadersToContext. The requestHeaders path in internal/proxy/http.go, the requestMetadata path in internal/proxy/grpc.go, and the Consume path in internal/unigrpc/grpc.go can forward an allowlisted value as a trusted backend header or metadata value. A remote client can spoof a header such as x-trusted-user for connect, refresh, subscribe, publish, RPC, and related proxy calls when the backend relies on that header for authentication or authorization. The unidirectional gRPC transport has no transport-level HTTP header that can override the emulated value. This issue is fixed in version 6.9.0.

## References
- https://github.com/centrifugal/centrifugo/releases/tag/v6.9.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71485.json
- https://github.com/centrifugal/centrifugo/security/advisories/GHSA-9468-v6mj-fppw
- https://nvd.nist.gov/vuln/detail/CVE-2026-71485
- https://github.com/centrifugal/centrifugo/commit/84d38cea1dd2efa24375a148817a974c8727f4b0
- https://github.com/centrifugal/centrifugo/pull/1182
