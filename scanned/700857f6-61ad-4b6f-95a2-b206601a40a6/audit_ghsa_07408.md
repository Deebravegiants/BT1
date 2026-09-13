# [H] Netty: [SpdyHttpDecoder] ByteBuf Reference Leak on RST_STREAM Leads to Native Memory Exhaustion

## Summary
Severity: High
Advisory: GHSA-jppx-w49h-x2qq
CVE: CVE-2026-56745
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-jppx-w49h-x2qq
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-http` — affected >=4.1.0.Final <4.1.136.Final

## Details
The `SpdyHttpDecoder` handler in Netty's SPDY-to-HTTP codec allocates a pooled `ByteBuf` when processing a client-initiated `SYN_STREAM` frame with `FLAG_FIN=0`, storing the partially-constructed `FullHttpRequest` in an internal map (`messageMap`) to accumulate subsequent `DATA` frames. When the remote peer sends an `RST_STREAM` for that stream, or when the accumulated content exceeds `maxContentLength`, the decoder removes the entry from the map but **never releases the pooled ByteBuf**, permanently leaking the allocated memory.

## References
- https://github.com/netty/netty/security/advisories/GHSA-jppx-w49h-x2qq
- https://nvd.nist.gov/vuln/detail/CVE-2026-56745
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty/commit/bb2ff68a1fb71cb4b0eb9a9e17b66c52aff680c6
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
