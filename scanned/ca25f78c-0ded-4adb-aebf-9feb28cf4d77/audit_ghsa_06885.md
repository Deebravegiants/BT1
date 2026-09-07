# [H] SIPSorcery: Malformed UDP packet on the RTP/ICE socket can remotely terminate a media session (DoS)

## Summary
Severity: High
Advisory: GHSA-28gm-jrmw-xx93
CVE: CVE-2026-54632
CWE: CWE-20, CWE-755
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-28gm-jrmw-xx93
Type: github-advisory

## Affected
- NuGet: `SIPSorcery` — affected >=0 <10.0.9

## Details
### Impact

A single malformed inbound UDP packet on the RTP/ICE socket can remotely terminate an active RTP or WebRTC media session. The packet receive handler indexes packet (and STUN attribute) bytes without sufficient length checks and throws, and the UDP receive loop converted any such exception into a channel `Close` rather than dropping the packet. One small, unauthenticated packet therefore ends the media session.

This is reachable during ICE connectivity checks — before the DTLS handshake and before any STUN `MESSAGE-INTEGRITY` verification. Because the RTP/ICE port is shared/advertised in the ICE candidates, a peer or on-path attacker can reach it (exposure is lower for a blind off-path attacker that must first learn the ephemeral port). Impact is availability only — no loss of confidentiality or integrity.

### Affected versions

NuGet package `SIPSorcery` `<= 10.0.8`.

### Patches

Fixed in `10.0.9`.

### Root cause

Two issues combine:

1. **Unchecked indexing of untrusted bytes.**
   - `RTPChannel.OnRTPPacketReceived` read `packet[1]` after only checking the packet was non-empty, so a 1-byte packet threw `IndexOutOfRangeException`.
   - `STUNAttribute.ParseMessageAttributes` passed a `null`/short value to the typed attribute parsers, and `STUNXORAddressAttribute` (and the non-XOR `STUNAddressAttribute`) then read `attributeValue[1]`, `AsSpan(2)` and `AsSpan(4)` with no length check. A STUN message carrying an `XOR-MAPPED-ADDRESS`, `XOR-PEER-ADDRESS` or `XOR-RELAYED-ADDRESS` attribute of length 0–7 threw (`NullReferenceException` for length 0, `IndexOutOfRangeException`/`ArgumentOutOfRangeException` for 1–7).

2. **The UDP receive loop closed the channel on any exception.** The catch-all in `UdpReceiver.EndReceiveFrom` called `Close()`, tearing down the channel, instead of dropping the offending packet and continuing. This was systemic: any unhandled exception anywhere in the packet pipeline (STUN, RTP, RTCP, DTLS demux, SRTP, TURN) became a channel teardown.

### Fix

- `UdpReceiver.EndReceiveFrom`: a non-socket exception now logs and drops the single packet and re-arms the receive loop (matching the existing `SIPUDPChannel` behaviour), instead of closing the channel. Genuine socket failures continue to be handled separately.
- `RTPChannel.OnRTPPacketReceived`: requires a minimum packet length (`RTPHeader.MIN_HEADER_LEN`) before indexing the discriminator bytes.
- STUN parsing: `ParseMessageAttributes` validates each attribute value length and skips malformed/truncated attributes; the XOR/address attribute constructors validate length defensively; `ParseSTUNMessage` no longer dereferences a null attribute list.

Regression tests were added covering the 1-byte packet (channel stays open and remains usable), short/zero-length XOR address attributes (0–7 bytes), and truncated STUN messages.

### Workarounds

None within the library short of upgrading. Restricting the RTP/ICE port to known peers at the network layer reduces exposure but does not eliminate it, since a negotiating peer can still trigger the condition.

### Credit

Responsibly reported by Lokhesh Ujhoodha.

## References
- https://github.com/sipsorcery-org/sipsorcery/security/advisories/GHSA-28gm-jrmw-xx93
- https://github.com/sipsorcery-org/sipsorcery/pull/1677
- https://github.com/sipsorcery-org/sipsorcery/commit/bdb76cbc0c7216e3126f743fb78e8525af56cea2
- https://github.com/sipsorcery-org/sipsorcery
