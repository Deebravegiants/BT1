# [M] Pre-handshake buffer capacity reservation based on attacker-claimed body length

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-h72h-ppcx-998p
Type: github-advisory

## Details
### Am I affected

You are affected if:

1. You run `zebrad` up to and including `v4.4.1`.
2. Your node accepts inbound P2P connections (`network.listen_addr` is set, which is the default).

### Summary

The P2P codec's `Codec::decode()` method calls `src.reserve(body_len + HEADER_LEN)` after parsing a 24-byte protocol header, using the attacker-claimed `body_len` field. This reserves up to `MAX_PROTOCOL_MESSAGE_LEN` (~2 MiB) of virtual buffer capacity per connection before any body bytes arrive and before the handshake completes.

However, `BytesMut::reserve()` sets virtual capacity without committing physical memory pages. The operating system does not allocate physical RAM until bytes are actually written into the buffer. Since the attacker never sends body bytes, the reserved capacity remains uncommitted. Reproduction of the reporter's PoC (256 threads, 30 seconds of sustained connections) showed negligible RSS impact on the Zebra process.

Zebra's existing mitigations further constrain the practical attack surface: per-IP connection limits (`max_connections_per_ip = 1`), a per-connection accept rate of approximately one per second, and a 3-second handshake timeout that cleans up idle connections.

### Details

At `zebra-network/src/protocol/external/codec.rs:406`, after parsing the 24-byte header and validating the network magic and body length against `MAX_PROTOCOL_MESSAGE_LEN`, the codec calls `src.reserve(body_len + HEADER_LEN)`. The codec is constructed on the bare TCP stream before `negotiate_version()` runs, so the reservation is reachable from any TCP peer that can send 24 bytes.

No legitimate Zcash handshake message (`version`, `verack`) is anywhere close to 2 MiB. The codec makes no distinction between pre-handshake and post-handshake message types when sizing the reservation.

### Patches

The fix defers large buffer reservations until after the handshake completes, or caps the per-message reservation for pre-handshake messages to what `version`/`verack` actually require.

### Workarounds

No workaround is needed. The existing per-IP rate limiting, handshake timeout, and connection limits effectively mitigate the practical impact.

### Impact

Minimal. The reservation affects virtual address space only, not physical memory. Zebra's existing connection-management mitigations (per-IP limits, accept rate, handshake timeout) further constrain the attack. The code path is worth cleaning up for defense-in-depth but does not produce a measurable denial-of-service effect.

### Credit

Reported by `@ouicate` via a private GitHub Security Advisory submission.

### References

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-h72h-ppcx-998p_
