# [M] Netty: [HttpContentEncoder] Unbounded Per-Connection Queue Growth via HTTP/1.1 Pipelining Leads to Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-q4f6-jm68-57ww
CVE: CVE-2026-59899
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-q4f6-jm68-57ww
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.136.Final

## Details
### Impact
`HttpContentEncoder` (the superclass of the production handler `HttpContentCompressor`) maintains a per-channel `ArrayDeque<CharSequence>` named `acceptEncodingQueue` that accumulates attacker-controlled data without any size limit. The queue is filled on the I/O thread for every inbound HTTP request and drained only when the application later writes a non-1xx response. This creates a resource exhaustion vulnerability when an attacker exploits HTTP/1.1 pipelining to flood the connection with requests faster than the application produces responses.

## References
- https://github.com/netty/netty/security/advisories/GHSA-q4f6-jm68-57ww
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
