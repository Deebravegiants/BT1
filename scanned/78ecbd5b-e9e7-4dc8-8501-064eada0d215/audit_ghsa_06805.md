# [M] webtransport-go: Memory Exhaustion Attack due to Buffering of Unknown Capsules

## Summary
Severity: Medium
Advisory: GHSA-g35j-m5xg-vh3q
CVE: CVE-2026-57497
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-g35j-m5xg-vh3q
Type: github-advisory

## Affected
- Go: `github.com/quic-go/webtransport-go` — affected >=0 <0.11.1

## Details
## Summary

An attacker can cause excessive memory allocation in webtransport-go by sending an unknown WebTransport capsule with a large payload. The implementation skips unknown capsules by reading the entire capsule body into memory, instead of draining it without retaining the data. This can lead to memory exhaustion.

## Impact

A misbehaving or malicious peer can cause a denial-of-service (DoS) attack against webtransport-go clients or servers by triggering excessive memory allocation, potentially leading to crashes or resource exhaustion.

## Details

WebTransport sessions use capsules on the HTTP/3 request stream. Unknown capsule types are ignored, but the capsule body still needs to be consumed before the next capsule can be parsed.

webtransport-go used `io.ReadAll` when skipping unknown capsules. Since the capsule reader is only limited by the capsule's declared length, a peer could send a large unknown capsule and cause the receiver to allocate memory for the full capsule body.

QUIC flow control limits buffered data, but it does not bound total allocation here, since reading the stream advances the flow control window while retaining the received bytes in memory.

## The Fix

webtransport-go now drains unknown capsules to `io.Discard` instead of buffering them. This consumes the capsule body so parsing can continue, without retaining the payload in memory.

## References
- https://github.com/quic-go/webtransport-go/security/advisories/GHSA-g35j-m5xg-vh3q
- https://github.com/quic-go/webtransport-go/pull/290
- https://github.com/quic-go/webtransport-go/commit/3aecd11736579530ff067651c30a543eb0b4b8c4
- https://github.com/quic-go/webtransport-go
- https://github.com/quic-go/webtransport-go/releases/tag/v0.11.1
