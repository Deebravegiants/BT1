# [M] Netty: QUIC stateless reset token material exposed through header-visible connection IDs

## Summary
Severity: Medium
Advisory: GHSA-cq4q-cv5g-r8q5
CVE: CVE-2026-50009
CWE: CWE-200, CWE-330
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-cq4q-cv5g-r8q5
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-classes-quic` — affected >=4.2.0.Final <4.2.15.Final

## Details
### Summary
Netty QUIC exposes the stateless reset token on the network path when using the default HMAC-based connection-ID and stateless-reset-token generators. The reset token for the server's current source connection ID can be derived from bytes that appear as the connection ID in QUIC headers after a source-CID rotation. An on-path attacker observing the headers can use the token to perform a Denial of Service by sending a spoofed Stateless Reset packet.

### Details
The sign-based connection ID generator (HmacSignQuicConnectionIdGenerator) and reset token generator (HmacSignQuicResetTokenGenerator) both evaluate HMAC-SHA256 with the same JVM-wide static key (io.netty.handler.codec.quic.Hmac).

During source CID rotation (QuicheQuicChannel.newSourceConnectionIds), the current server source CID C is used as input to produce the next CID N. The stateless reset token for C is defined over HMAC(K, C), specifically the first 16 bytes. The next CID N is the first L bytes of the same digest, where L = |C|.

Whenever L ≥ 16, the first 16 bytes of N are exactly the stateless reset token for C. Because N is carried in QUIC headers as a connection ID, an observer can read the headers and learn the reset token without decrypting the payload.

This directly violates RFC 9000
https://datatracker.ietf.org/doc/html/rfc9000#name-calculating-a-stateless-res: `The stateless reset token MUST be difficult to guess.`
Additionally https://datatracker.ietf.org/doc/html/rfc9000#name-stateless-reset-oracle

### Impact
Information Disclosure and Denial of Service. An on-path attacker can obtain the stateless reset token from the connection ID header and attempt to abruptly close the client side of the connection by sending a spoofed Stateless Reset datagram.

## References
- https://github.com/netty/netty/security/advisories/GHSA-cq4q-cv5g-r8q5
- https://nvd.nist.gov/vuln/detail/CVE-2026-50009
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
