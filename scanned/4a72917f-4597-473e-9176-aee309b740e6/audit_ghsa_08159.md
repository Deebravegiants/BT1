# [M] webtransport-go: Memory Exhaustion Attack due to Missing Length Check in WT_CLOSE_SESSION Capsule

## Summary
Severity: Medium
Advisory: GHSA-g6x7-jq8p-6q9q
CVE: CVE-2026-21434
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-g6x7-jq8p-6q9q
Type: github-advisory

## Affected
- Go: `github.com/quic-go/webtransport-go` — affected >=0.3.0 <0.10.0

## Details
## Summary
An attacker can cause excessive memory consumption in webtransport-go's session implementation by sending a WT_CLOSE_SESSION capsule containing an excessively large Application Error Message. The implementation does not enforce the draft-mandated limit of 1024 bytes on this field, allowing a peer to send an arbitrarily large message payload that is fully read and stored in memory.

This allows an attacker to consume an arbitrary amount of memory. The attacker must transmit the full payload to achieve the memory consumption, but the lack of any upper bound makes large-scale attacks feasible given sufficient bandwidth.

## Details
WebTransport over HTTP/3, as defined in draft-ietf-webtrans-http3, uses the WT_CLOSE_SESSION capsule to signal session termination with an optional detailed error. The draft specifies that the length of the Application Error Message in this capsule MUST NOT exceed 1024 bytes.
In affected versions of webtransport-go, the parser does not enforce this 1024-byte maximum when processing incoming WT_CLOSE_SESSION capsules. A peer can send a capsule with an excessively large payload, forcing the recipient to allocate and buffer the full amount of transmitted data without bound.

## The Fix
webtransport-go now limits the length of the parsed Application Error Message to 1024 bytes in WT_CLOSE_SESSION capsules by reading no more than this amount. This prevents excessive memory consumption.

## References
- https://github.com/quic-go/webtransport-go/security/advisories/GHSA-g6x7-jq8p-6q9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-21434
- https://github.com/quic-go/webtransport-go
- https://github.com/quic-go/webtransport-go/releases/tag/v0.10.0
