# [M] webtransport-go: Memory Exhaustion Attack due to Missing Cleanup of Streams Map

## Summary
Severity: Medium
Advisory: GHSA-2f2x-8mwp-p2gc
CVE: CVE-2026-21438
CWE: CWE-401, CWE-459
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-2f2x-8mwp-p2gc
Type: github-advisory

## Affected
- Go: `github.com/quic-go/webtransport-go` — affected >=0 <0.10.0

## Details
## Summary
An attacker can cause unbounded memory consumption repeatedly creating and closing many WebTransport streams. Closed streams were not removed from an internal session map, preventing garbage collection of their resources.

## Details
webtransport-go maintains an internal map tracking WebTransport streams (both unidirectional and bidirectional) belonging to a session. In affected versions, entries for closed streams were not removed from this map, causing the map to grow indefinitely as streams were created and closed.

A malicious peer can exploit this by opening large numbers of streams and closing them, leading to steady memory growth proportional to the number of closed streams.

## The Fix
webtransport-go now removes closed streams from the internal map upon closure. This allows the associated resources to be garbage collected, bounding memory usage to active streams only.

## References
- https://github.com/quic-go/webtransport-go/security/advisories/GHSA-2f2x-8mwp-p2gc
- https://nvd.nist.gov/vuln/detail/CVE-2026-21438
- https://github.com/quic-go/webtransport-go
- https://github.com/quic-go/webtransport-go/releases/tag/v0.10.0
