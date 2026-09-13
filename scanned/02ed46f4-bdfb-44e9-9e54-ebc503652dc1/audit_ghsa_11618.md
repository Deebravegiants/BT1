# [H] Yamux vulnerable to remote Panic via malformed Data frame with SYN set and len = 262145

## Summary
Severity: High
Advisory: GHSA-vxx9-2994-q338
CVE: CVE-2026-32314
CWE: CWE-248, CWE-617
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-vxx9-2994-q338
Type: github-advisory

## Affected
- crates.io: `yamux` — affected >=0 <0.13.10

## Details
### Summary
The Rust implementation of Yamux can panic when processing a crafted inbound Data frame that sets SYN and uses a body length greater than DEFAULT_CREDIT (e.g. 262145).
On the first packet of a new inbound stream, stream state is created and a receiver is queued before oversized-body validation completes. When validation fails, the temporary stream is dropped and cleanup may call remove(...).expect("stream not found"), triggering a panic in the connection state machine.
This is remotely reachable over a normal Yamux session and does not require authentication. kind of vulnerability is it? Who is 
#### Attack Scenario  
An attacker that can establish a Yamux session with a target node can crash the target by sending a single validly encoded Yamux Data|SYN frame with an oversized body:
1. Establish a standard authenticated transport session that negotiates Yamux.
2. Send one Yamux frame with:
   - Tag = Data
   - Flags = SYN
   - StreamId = 1 (or any new inbound stream id)
   - Length = DEFAULT_CREDIT + 1 (e.g. 262145)
   - Body of matching size
This can trigger a panic (stream not found) and terminate the process, depending on host application panic policy.
### Patches
Users should upgrade to `yamux` `v0.13.10`

This vulnerability was originally submitted by @revofusion to the Ethereum Foundation bug bounty program

## References
- https://github.com/libp2p/rust-yamux/security/advisories/GHSA-vxx9-2994-q338
- https://nvd.nist.gov/vuln/detail/CVE-2026-32314
- https://github.com/libp2p/rust-yamux
