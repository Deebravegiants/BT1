# [H] Netty: SNI Routing Bypass via Fragmented TLS ClientHello Causing Fallback to Default SslContext

## Summary
Severity: High
Advisory: CVE-2026-75595
Aliases: GHSA-c4c3-7fpv-j4q5
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-75595
Type: osv

## Details
Netty is an asynchronous, event-driven network application framework. Prior to 4.1.137.Fina and 4.2.17.Final, io.netty.handler.ssl.SslClientHelloHandler#decode checks the wrong offset before reading the four-byte TLS handshake header, so a ClientHello whose handshake header spans records can cause an IndexOutOfBoundsException and invoke select(ctx, null). This selects the default SslContext instead of the SNI-specific context. In deployments where per-SNI clientAuth=REQUIRE is the sole mutual TLS gate, the default SslContext uses clientAuth=NONE or clientAuth=OPTIONAL, and no application-layer certificate verification exists, an unauthenticated remote attacker can bypass the protected route's mutual TLS requirement. This issue is fixed in versions 4.1.137.Final and 4.2.17.Final.

## References
- https://github.com/netty/netty/releases/tag/netty-4.1.137.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.17.Final
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75595.json
- https://github.com/netty/netty/security/advisories/GHSA-c4c3-7fpv-j4q5
- https://nvd.nist.gov/vuln/detail/CVE-2026-75595
- https://github.com/netty/netty/commit/1b5abc6443b63726c72cdd285af2feb7ddbb8ff7
- https://github.com/netty/netty/commit/9e0519239108a69b7e9bbc5e9182ee139a0d7961
- https://github.com/netty/netty/pull/17213
- https://github.com/netty/netty/pull/17217
