# [M] HTTP/2 connection-window starvation pins Plug processes indefinitely in Bandit

## Summary
Severity: Medium
Advisory: CVE-2026-74836
Aliases: EEF-CVE-2026-74836, GHSA-xj8g-532w-jv94
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-74836
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in mtrudel bandit allows an unauthenticated remote attacker to pin an unbounded number of HTTP/2 stream processes indefinitely via connection-level flow control. When a stream's response body outruns the HTTP/2 connection-level send window (default 65,535 bytes, shared across all streams on the connection), Bandit.HTTP2.Connection queues the remaining bytes and a reply closure in pending_sends and the stream process blocks forever inside a synchronous call to the connection process. Nothing bounds that wait and nothing purges the queue: a client RST_STREAM for the blocked stream is delivered to its mailbox but never read while it is stuck inside the call, so cancelling frees nothing, and periodic PING frames keep the transport-level read timeout from ever firing. The equivalent block on the stream-level send window is already bounded at 15 seconds; the connection-level path had no such bound.

Each stalled stream pins its process, Plug state, and any resource the Plug holds across the blocked write, such as a pooled upstream connection in a reverse-proxy Plug. The attacker chooses any endpoint whose response exceeds the connection window (common for most non-trivial payloads), grants a generous stream-level window so only the connection window limits it, and keeps the connection alive with periodic PINGs; the primitive is repeatable across streams and connections at the cost of one idle socket each.

This issue affects bandit: from 0.3.4 before 1.12.5.

## References
- https://cna.erlef.org/cves/CVE-2026-74836.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-74836
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74836.json
- https://github.com/mtrudel/bandit/security/advisories/GHSA-xj8g-532w-jv94
- https://nvd.nist.gov/vuln/detail/CVE-2026-74836
- https://github.com/mtrudel/bandit/commit/f6914aad14bb1365dd6f306aa592cfb0819bed3e
- https://github.com/mtrudel/bandit
