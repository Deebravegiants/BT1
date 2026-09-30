# [H] libp2p-quic: Remote panic via certificate expiry race during QUIC handshake

## Summary
Severity: High
Advisory: GHSA-5hq8-qhww-jm7q
Aliases: CVE-2026-61544
Package: libp2p-quic
Published: 2026-09-15
Source: https://osv.dev/vulnerability/GHSA-5hq8-qhww-jm7q
Type: chain-advisory

## Affected
- crates.io: `libp2p-quic` — affected >=0 <0.13.1

## Details
### Summary

`libp2p-quic` can panic on an inbound QUIC handshake if a malicious peer presents a valid, short lived libp2p TLS certificate and delays the final TLS 1.3 handshake fragment until the certificate expires.

This is remotely reachable by a network peer and can crash applications exposing a libp2p QUIC listener.

### Details
During the TLS handshake, `libp2p-tls` parses and validates the peer certificate. After Quinn reports handshake completion, `libp2p-quic` re-parses the same certificate in the post-handshake upgrade path and assumes this cannot fail:

https://github.com/libp2p/rust-libp2p/blob/969b707bf1177ebebd1febc285c3fd22793b95c5/transports/quic/src/connection/connecting.rs#L65-L66

However, `libp2p_tls::certificate::parse()` re-runs certificate verification on every call, including a wall-clock validity check. A certificate that was valid during the first handshake time parse can expire before the second post-handshake parse, causing the `expect(...)` to panic.


### PoC
A malicious peer can trigger this by:
1. Opening a QUIC connection to a libp2p QUIC listener.
2. Presenting a valid libp2p TLS certificate with a very short lifetime.
3. Allowing the initial handshake-time certificate validation to succeed.
4. Withholding the final client handshake fragment packet until after the certificate expires, but before the QUIC handshake timeout elapses.
5. The listener completes the handshake and hits the post-handshake certificate re-parse, which panics.

### Impact
Remote unauthenticated denial of service. Any application exposing an affected `libp2p-quic` listener can be crashed by a network peer that performs a valid-looking QUIC/TLS handshake with attacker-controlled timing. No malformed packets are required.

## References
- https://github.com/libp2p/rust-libp2p/security/advisories/GHSA-5hq8-qhww-jm7q
- https://github.com/libp2p/rust-libp2p/pull/6525
- https://github.com/libp2p/rust-libp2p/commit/212f3774af048e2cecfb2e6b1e08477685e52b22
- https://github.com/libp2p/rust-libp2p/commit/e8f35e12c2418b04df6e9cdf036005e8aee3c7a2
- https://github.com/libp2p/rust-libp2p
