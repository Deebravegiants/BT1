# [H] Netty: [codec-haproxy] Signed-Byte Sentinel Collision in HAProxyMessageDecoder Leads to Unbounded Memory Exhaustion

## Summary
Severity: High
Advisory: GHSA-q6cq-mhr2-jmr5
CVE: CVE-2026-55851
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-q6cq-mhr2-jmr5
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-haproxy` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-haproxy` — affected >=4.1.0.Final <4.1.136.Final

## Details
The `HAProxyMessageDecoder` in netty's `codec-haproxy` module performs protocol version detection by reading the 13th byte of the inbound stream as a signed Java `byte` and widening it to `int` without masking. When an attacker sends a PROXY protocol v2 binary prefix (`0D 0A 0D 0A 00 0D 0A 51 55 49 54 0A`) followed by version byte `0xFF`, the sign extension produces `-1`, which collides with the decoder's "need more data" sentinel value. This collision traps the decoder in a version-detection loop where it perpetually requests more data without consuming any bytes, never instantiates the `HeaderExtractor` that enforces header size limits, and causes `ByteToMessageDecoder` to accumulate all subsequent inbound bytes into an unbounded `cumulation` buffer until the JVM exhausts its direct memory allocation.

## References
- https://github.com/netty/netty/security/advisories/GHSA-q6cq-mhr2-jmr5
- https://nvd.nist.gov/vuln/detail/CVE-2026-55851
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty/commit/bb2ff68a1fb71cb4b0eb9a9e17b66c52aff680c6
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
