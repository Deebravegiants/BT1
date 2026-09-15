# [H] quic-go: Panic occurs when queuing undecryptable packets after handshake completion

## Summary
Severity: High
Advisory: GHSA-47m2-4cr7-mhcw
CVE: CVE-2025-59530
CWE: CWE-617, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-47m2-4cr7-mhcw
Type: github-advisory

## Affected
- Go: `github.com/quic-go/quic-go` — affected >=0 <0.49.1
- Go: `github.com/quic-go/quic-go` — affected >=0.50.0 <0.54.1

## Details
## Summary

A misbehaving or malicious server can trigger an assertion in a quic-go client (and crash the process) by sending a premature HANDSHAKE_DONE frame during the handshake.

## Impact

A misbehaving or malicious server can cause a denial-of-service (DoS) attack on the quic-go client by triggering an assertion failure, leading to a process crash. This requires no authentication and can be exploited during the handshake phase. Observed in the wild with certain server implementations (e.g. Solana's Firedancer QUIC).

## Affected Versions

- All versions prior to v0.49.1 (for the 0.49 branch)
- Versions v0.50.0 to v0.54.0 (inclusive)
- Fixed in v0.49.1, v0.54.1, and v0.55.0 onward

Users are recommended to upgrade to the latest patched version in their respective maintenance branch or to v0.55.0 or later.

## Details

For a regular 1-RTT handshake, QUIC uses three sets of keys to encrypt / decrypt QUIC packets:

- Initial keys (derived from a static key and the connection ID)
- Handshake keys (derived from the client's and server's key shares in the TLS handshake)
- 1-RTT keys (derived when the TLS handshake finishes)

On the client side, Initial keys are discarded when the first Handshake packet is sent. Handshake keys are discarded when the server's HANDSHAKE_DONE frame is received, as specified in section 4.9.2 of RFC 9001. Crucially, Initial keys are always dropped before Handshake keys in a standard handshake.

Due to packet reordering, it is possible to receive a packet with a higher encryption level before the key for that encryption level has been derived. For example, the server's Handshake packets (containing, among others, the TLS certificate) might arrive before the server's Initial packet (which contains the TLS ServerHello). In that case, the client queues the Handshake packets and decrypts them as soon as it has processed the ServerHello and derived Handshake keys.

After completion of the handshake, Initial and Handshake packets are not needed anymore and will be dropped. quic-go implements an [assertion](https://github.com/quic-go/quic-go/blob/v0.55.0/connection.go#L2682-L2685) that no packets are queued after completion of the handshake.

A misbehaving or malicious server can trigger this assertion, and thereby cause a panic, by sending a HANDSHAKE_DONE frame before actually completing the handshake. In that case, Handshake keys would be dropped before Initial keys.

This can only happen if the server implementation is misbehaving: the server can only complete the handshake after receiving the client's TLS Finished message (which is sent in Handshake packets).

## The Fix

quic-go needs to be able to handle misbehaving server implementations, including those that prematurely send a HANDSHAKE_DONE frame. We now discard Initial keys when receiving a HANDSHAKE_DONE frame, thereby correctly handling premature HANDSHAKE_DONE frames. The fix was implemented in https://github.com/quic-go/quic-go/pull/5354.

## References
- https://github.com/quic-go/quic-go/security/advisories/GHSA-47m2-4cr7-mhcw
- https://nvd.nist.gov/vuln/detail/CVE-2025-59530
- https://github.com/quic-go/quic-go/pull/5354
- https://github.com/quic-go/quic-go/commit/bc5bccf10fd02728eef150683eb4dfaa5c0e749c
- https://github.com/quic-go/quic-go/commit/ce7c9ea8834b9d2ed79efa9269467f02c0895d42
- https://github.com/quic-go/quic-go
- https://github.com/quic-go/quic-go/blob/v0.55.0/connection.go#L2682-L2685
- https://pkg.go.dev/vuln/GO-2025-4017
