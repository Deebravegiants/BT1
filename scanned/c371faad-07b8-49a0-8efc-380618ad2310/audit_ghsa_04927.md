# [H] Netty's Default QUIC token handler accepts any client-supplied token

## Summary
Severity: High
Advisory: GHSA-cmm3-54f8-px4j
CVE: CVE-2026-44894
CWE: CWE-940
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-cmm3-54f8-px4j
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-classes-quic` — affected >=4.2.0.Final <4.2.15.Final

## Details
NoQuicTokenHandler is the tokenHandler used when the application does not set one. Its writeToken() returns false (server will not send Retry — acceptable), but validateToken() unconditionally `return 0`. In QuicheQuicServerCodec.handlePacket(), a non-negative return from validateToken() is interpreted as 'token is valid, ODCID starts at offset 0', causing the server to call quiche_accept as if the client's address had been validated by a Retry round-trip. Per RFC 9000 §8.1, a validated address lifts the 3× anti-amplification send limit. Thus any attacker who includes ANY non-empty token bytes in an Initial packet — with a spoofed victim source IP — causes the Netty server to treat the victim as validated and reflect full-size handshake flights (certificates, etc.) toward it without the 3× cap. The correct 'no token handler' semantics would be to return -1 (invalid) so the normal un-validated path and amplification limit apply.

## References
- https://github.com/netty/netty/security/advisories/GHSA-cmm3-54f8-px4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-44894
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
