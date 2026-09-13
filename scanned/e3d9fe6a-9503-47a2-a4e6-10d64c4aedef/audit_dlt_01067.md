# [H] Gossipsub PRUNE.backoff Duration Overflow

## Summary
Severity: High
Chain: libp2p-gossipsub
Component: libp2p-gossipsub
CVE: CVE-2026-33040
CWE: Integer Overflow or Wraparound
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-gc42-3jg7-rxr2
Type: github-advisory

## Details
### Summary
The Rust libp2p Gossipsub implementation accepts attacker-controlled PRUNE backoff values and may perform unchecked time arithmetic when storing backoff state.
A specially crafted PRUNE control message with an extremely large backoff (e.g. u64::MAX) can lead to Duration/Instant overflow during backoff update logic, triggering a panic in the networking state machine. This is remotely reachable over a normal libp2p connection and does not require authentication.

### Attack Scenario
An attacker that can establish a libp2p Gossipsub session with a target node can crash the target by sending a single crafted PRUNE control message:
1. Establish a standard libp2p transport session and negotiate a stream multiplexer.
2. Open a Gossipsub stream and negotiate the meshsub protocol.
3. Send one protobuf RPC containing ControlPrune with a very large backoff value (e.g. 18446744073709551615 / u64::MAX).
When processed, the oversized backoff can reach time-update logic that adds Duration::from_secs(backoff) to Instant::now(), causing overflow and panic.

### Impact
Remote unauthenticated denial of service.
Any application exposing a libp2p Gossipsub listener and using the affected backoff-handling path can be crashed by a network attacker that can reach the service port. The attack can be repeated by reconnecting and replaying the crafted control message.
### Patches
Users should upgrade to a release that hardens Gossipsub backoff handling.

This vulnerability was originally submitted by @revofusion to the Ethereum Foundation bug bounty program
