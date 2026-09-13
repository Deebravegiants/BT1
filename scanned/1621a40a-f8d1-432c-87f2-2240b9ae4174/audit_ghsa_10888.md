# [H] Yamux vulnerable to remote Panic via malformed WindowUpdate credit

## Summary
Severity: High
Advisory: GHSA-4w32-2493-32g7
CVE: CVE-2026-31814
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-4w32-2493-32g7
Type: github-advisory

## Affected
- crates.io: `yamux` — affected >=0.13.0 <0.13.9

## Details
### Sumary
The Rust implementation of Yamux accepts `WindowUpdate` credit values from the remote peer and applies them to per-stream send-window state.  
A specially crafted `WindowUpdate` can cause arithmetic overflow in send-window accounting, which triggers a panic in the connection state machine. This is remotely reachable over a normal network connection and does not require authentication.
#### Attack Scenario  
An attacker that can establish a Yamux session with a target node can crash the target by sending two validly encoded Yamux frames:
1. Open a stream (e.g. DATA + SYN) so the stream exists with initial send-window state (`DEFAULT_CREDIT`).
2. Send a WindowUpdate on that stream with a very large credit value (e.g. 0xFFFF_0000) such that adding credit to the current send-window overflows u32.
### Impact
Remote unauthenticated denial of service.  
An attacker can repeatedly trigger panics by reconnecting and replaying the crafted frame sequence.
### Patches
Users should upgrade to `yamux` `v0.13.9`

This vulnerability was originally submitted by @revofusion to the Ethereum Foundation bug bounty program

## References
- https://github.com/libp2p/rust-yamux/security/advisories/GHSA-4w32-2493-32g7
- https://nvd.nist.gov/vuln/detail/CVE-2026-31814
- https://github.com/libp2p/rust-yamux/pull/221
- https://github.com/libp2p/rust-yamux/commit/b1aae09d60c0bd6a5915a5448f4e8cbc5174db53
- https://github.com/libp2p/rust-yamux
- https://github.com/libp2p/rust-yamux/releases/tag/yamux-v0.13.9
