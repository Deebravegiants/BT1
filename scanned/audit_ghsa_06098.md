# [H] Netty: Memory Exhaustion in SctpMessageCompletionHandler

## Summary
Severity: High
Advisory: GHSA-2qj4-mmr9-4v2f
CVE: CVE-2026-59902
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-2qj4-mmr9-4v2f
Type: github-advisory

## Affected
- Maven: `io.netty:netty-transport-sctp` — affected >=4.2.0.Final <4.2.17.Final
- Maven: `io.netty:netty-transport-sctp` — affected >=0 <4.1.137.Final

## Details
### Summary
SctpMessageCompletionHandler does not limit the total size of buffered fragments, allowing an unauthenticated attacker to cause an OutOfMemoryError by sending large SCTP fragments.

### Details
`io.netty.handler.codec.sctp.SctpMessageCompletionHandler` buffers fragments for incomplete SCTP messages. The fix for CVE-2026-46340 fixed unbounded memory growth by introducing limits on the number of concurrent incomplete messages (maxIncompleteSctpMessages) and the number of fragments per message (maxFragments).

While the count of fragments is now bounded, the handler still does not enforce a maximum size in bytes.

With the default limits of 128 messages and 128 fragments, and a typical max SCTP chunk size of 64KB, an attacker can consume up to ~1GB per connection. By opening a small number of concurrent connections, an attacker can easily exhaust the server's memory, causing an OutOfMemoryError.

### Impact
Memory Exhaustion. Any application using Netty's SCTP transport with SctpMessageCompletionHandler is impacted.

## References
- https://github.com/netty/netty/security/advisories/GHSA-2qj4-mmr9-4v2f
- https://github.com/netty/netty/pull/17213
- https://github.com/netty/netty/pull/17217
- https://github.com/netty/netty/commit/1b5abc6443b63726c72cdd285af2feb7ddbb8ff7
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.137.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.17.Final
