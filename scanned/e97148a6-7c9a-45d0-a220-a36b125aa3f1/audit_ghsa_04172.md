# [H] Netty: SCTP reassembly nests buffers without bound

## Summary
Severity: High
Advisory: GHSA-5xrh-qmmq-w6ch
CVE: CVE-2026-46340
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-5xrh-qmmq-w6ch
Type: github-advisory

## Affected
- Maven: `io.netty:netty-transport-sctp` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-transport-sctp` — affected >=0 <4.1.135.Final

## Details
For each non-complete SctpMessage fragment the handler does `fragments.put(streamId, Unpooled.wrappedBuffer(frag, byteBuf))`, wrapping the previous accumulator and the new slice into a *new* CompositeByteBuf every time. After N fragments the accumulator is an N-deep chain of composites, each holding references and component arrays; readableBytes()/getBytes() on the final buffer recurse N levels. There is no limit on N, on total bytes, or on the number of streamIdentifiers an attacker can open (each gets its own map entry). A peer that never sets the `complete` flag can grow this structure indefinitely from tiny 1-byte DATA chunks.

## References
- https://github.com/netty/netty/security/advisories/GHSA-5xrh-qmmq-w6ch
- https://nvd.nist.gov/vuln/detail/CVE-2026-46340
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
