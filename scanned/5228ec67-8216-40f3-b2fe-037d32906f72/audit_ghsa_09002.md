# [H] ex_webrtc client-role handshake is missing DTLS peer fingerprint validation

## Summary
Severity: High
Advisory: GHSA-qwfw-ggxw-577c
CVE: CVE-2026-44700
CWE: CWE-295
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-qwfw-ggxw-577c
Type: github-advisory

## Affected
- Hex: `ex_webrtc` — affected >=0 <0.15.1
- Hex: `ex_webrtc` — affected >=0.16.0 <0.16.1

## Details
### Summary
Missing DTLS peer certificate fingerprint validation in the DTLS client (active) role removes one side of WebRTC's mutual authentication. The bug is not independently exploitable for media interception in standard deployments, but enables a full man-in-the-middle attack when chained with insecure signalling or a peer with similar validation gaps.

### Details
`ex_webrtc` validates the DTLS peer's certificate fingerprint against the value advertised in the SDP offer/answer when acting as the DTLS server (passive role). When acting as the DTLS client (active role) -- the default when answering a remote offer with `a=setup:actpass`, which is what browsers always send -- the fingerprint check was skipped on the handshake-completion code path that returns no outgoing packets. This is the most common deployment mode (e.g., an SFU or media server answering a browser's offer).

All released versions prior to 0.15.1 and 0.16.1 are affected. No backports to older lines are planned -- users should upgrade to 0.15.1 or 0.16.1.

### Impact
The bug eliminates one half of WebRTC's mutual DTLS authentication. The security of the media and data-channel encryption then rests entirely on the remote peer's fingerprint check.

On its own, the bug does **not** allow:

- Passive eavesdropping on SRTP media.
- A network-positioned attacker to intercept media against a standards-compliant browser peer over a TLS-protected signalling channel -- the browser's fingerprint check prevents the second leg of the MITM from succeeding.

The bug **does** enable a full MITM on media and data channels when combined with any of:

- Insecure signalling (HTTP / plain WebSocket) allowing SDP rewrite in transit.
- A compromised or malicious signalling server.
- A peer implementation with a similar fingerprint-validation gap.

Both audio/video media (SRTP) and data channels (SCTP-over-DTLS) are affected.

### Patches
- `0.15.1` (for the 0.15.x line)
- `0.16.1` (for the 0.16.x line)

### Workarounds
None. Upgrade is required.

### Resources
- [Issue](https://github.com/elixir-webrtc/ex_webrtc/issues/249)
- [PR](https://github.com/elixir-webrtc/ex_webrtc/pull/250)
- [Release 0.15.1](https://github.com/elixir-webrtc/ex_webrtc/releases/tag/v0.15.1)
- [Release 0.16.1](https://github.com/elixir-webrtc/ex_webrtc/releases/tag/v0.16.1)

## References
- https://github.com/elixir-webrtc/ex_webrtc/security/advisories/GHSA-qwfw-ggxw-577c
- https://nvd.nist.gov/vuln/detail/CVE-2026-44700
- https://github.com/elixir-webrtc/ex_webrtc/issues/249
- https://github.com/elixir-webrtc/ex_webrtc/pull/250
- https://github.com/elixir-webrtc/ex_webrtc/commit/658c63221a869fb12bb9989599c3688751b0531b
- https://github.com/elixir-webrtc/ex_webrtc
- https://github.com/elixir-webrtc/ex_webrtc/releases/tag/v0.15.1
- https://github.com/elixir-webrtc/ex_webrtc/releases/tag/v0.16.1
