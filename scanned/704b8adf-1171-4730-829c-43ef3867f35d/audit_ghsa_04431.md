# [H] Netty: SNI handler pre-allocates up to 16 MiB from nine attacker bytes

## Summary
Severity: High
Advisory: GHSA-x4gw-5cx5-pgmh
CVE: CVE-2026-45416
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-x4gw-5cx5-pgmh
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-handler` — affected >=0 <4.1.135.Final

## Details
SslClientHelloHandler.decode() reads the 24-bit TLS handshake length and, when the ClientHello does not fit in the first record, eagerly allocates `ctx.alloc().buffer(handshakeLength)` (line 161). The guard at line 140 is `handshakeLength > maxClientHelloLength && maxClientHelloLength != 0`, and the commonly-used SniHandler/AbstractSniHandler constructors (SniHandler(Mapping), SniHandler(AsyncMapping), AbstractSniHandler()) pass maxClientHelloLength=0 and handshakeTimeoutMillis=0, so the length guard is disabled and no timeout is scheduled. A 16 MiB request exceeds the default pooled chunk size and becomes a huge/unpooled allocation performed immediately. The buffer is retained in the handler until the channel closes.

## References
- https://github.com/netty/netty/security/advisories/GHSA-x4gw-5cx5-pgmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45416
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
