# [M] Mempool transaction admission denial via single-peer inbound queue saturation

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-52732
CWE: Allocation of Resources Without Limits or Throttling
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-4fc2-h7jh-287c
Type: github-advisory

## Details
### Am I affected

You are affected if:

1. You run `zebrad` up to and including `v4.4.1`.
2. Your node accepts inbound P2P connections (`network.listen_addr` is set, which is the default).
3. Your node's mempool is active (node is synced near the chain tip).

All default configurations are affected.

### Summary

A single unauthenticated P2P peer can monopolize all 25 inbound mempool download/verification slots (`MAX_INBOUND_CONCURRENCY`) by advertising fake transaction IDs. While the slots are occupied, all other inbound transactions from honest peers and local RPC `sendrawtransaction` calls are rejected with `MempoolError::FullQueue`. The attacker peer is never scored for misbehavior and is not disconnected, allowing sustained denial of mempool admission.

### Details

The mempool download/verification pipeline at `zebrad/src/components/mempool/downloads.rs` uses a single bounded pool of 25 concurrent tasks. Three architectural gaps combine to produce the vulnerability:

1. No per-peer accounting: the 25 slots are shared across all peers with no cap on how many a single peer can hold.
2. No overload signaling: when `FullQueue` is returned, the inbound service at `zebrad/src/components/inbound.rs` maps it to `Response::Nil`, hiding the overload from the peer connection layer. The existing `handle_inbound_overload` disconnection logic never fires.
3. No misbehavior attribution: peer identity is not carried through the `Gossip` type into the download pipeline, so verification failures cannot be attributed to the originating peer.

The attacker sends `inv` messages advertising fake transaction IDs. Zebra queues download tasks for each ID. The attacker stays silent; each slot is held until the `TRANSACTION_DOWNLOAD_TIMEOUT` (20 seconds) fires. The attacker periodically sends fresh `inv` waves to re-fill slots as they expire.

Two additional slot-holding techniques have been independently demonstrated: invalid-prevout transactions that park in `AwaitOutput` for 60 seconds, and expensive shielded proof verification with auth-variant cache bypass. All three techniques are addressed by the same per-peer accounting fix.

### Patches

TBD.

The fix adds per-peer queue accounting to the mempool download pipeline. A single peer is limited to a fraction of `MAX_INBOUND_CONCURRENCY` (e.g., 5 slots out of 25). `FullQueue` is surfaced as an overload signal to the peer connection layer. Peer identity is plumbed through the `Gossip` type for misbehavior attribution.

### Workarounds

There is no complete configuration-level workaround. Reducing `network.peerset_initial_target_size` limits the total inbound peer count but does not prevent a single peer from holding all mempool slots.

### Impact


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-4fc2-h7jh-287c_
