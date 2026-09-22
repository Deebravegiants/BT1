# [M] Netty: Fragmented ClientHello records trigger quadratic pre-handshake reassembly in default SNI parsing

## Summary
Severity: Medium
Advisory: CVE-2026-75596
Aliases: GHSA-fccg-mwvh-qqg4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-75596
Type: osv

## Details
Netty is an asynchronous, event-driven network application framework. Prior to 4.1.137.Final and 4.2.17.Final, the default io.netty.handler.ssl.SniHandler constructors use the pre-handshake ClientHello aggregation path in handler/src/main/java/io/netty/handler/ssl/SslClientHelloHandler.java at io.netty.handler.ssl.SslClientHelloHandler#decode, where handshakeBuffer.clear() and writeBytes() recopy all previously received body bytes for every additional TLS record. An unauthenticated remote peer can advertise a large ClientHello and deliver its body in thousands of tiny records, causing quadratic CPU work on the event loop before the TLS handshake completes and degrading TLS handling for other clients. This issue is fixed in versions 4.1.137.Final and 4.2.17.Final.

## References
- https://github.com/netty/netty/releases/tag/netty-4.1.137.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.17.Final
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75596.json
- https://github.com/netty/netty/security/advisories/GHSA-fccg-mwvh-qqg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-75596
- https://github.com/netty/netty/commit/1b5abc6443b63726c72cdd285af2feb7ddbb8ff7
- https://github.com/netty/netty/commit/9e0519239108a69b7e9bbc5e9182ee139a0d7961
- https://github.com/netty/netty/pull/17213
- https://github.com/netty/netty/pull/17217
