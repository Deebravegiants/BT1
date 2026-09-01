# [H] Uncapped shielded verification cost lets peer-pushed V6 transactions stall block verification

## Summary
Severity: High
Chain: Zcash
Component: ZcashFoundation/zebra
CWE: Uncontrolled Resource Consumption, Allocation of Resources Without Limits or Throttling
Published: 2026-08-17
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-2p4c-3q4q-p463
Type: github-advisory

## Details
# Uncapped shielded verification cost lets peer-pushed V6 transactions stall block verification

| Field | Value |
|---|---|
| Severity | High |
| CVSS 3.1 | AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (7.5) |
| CWE | CWE-405 (Asymmetric Resource Consumption); CWE-770 (Allocation of Resources Without Limits or Throttling) |
| Affected versions | zebrad through v6.2.0, on networks where NU6.3 (Ironwood) is active |
| Patched versions | v6.2.1 |
| Reporter credit | @craftsoldier |
| GHSA | GHSA-2p4c-3q4q-p463 |
| Fix PR | #11053 (ZIP-317 pre-verification check), #11054 (invalid-proof peer ban) |

## Am I affected?

You are affected if you run zebrad v6.2.0 or earlier with default peer-to-peer networking on a network where NU6.3 (Ironwood) is active. The condition is reachable by any peer that can connect and send transactions; no authentication or special privileges are required. While the attack continues, a node with few cores stalls block verification and falls behind the chain tip; it recovers when the attack stops. There is no crash, no consensus fault, and no loss of funds. Upgrade to v6.2.1 or later.

## Summary

When Zebra verifies a V6 transaction offered by a peer for the mempool, it performs full Halo2 proof verification on the shielded bundles before rejecting cryptographically invalid proofs. The mempool downloader caps concurrent verifications by transaction count (5 per advertising peer, 500 global), not by verification cost. NU6.3 (Ironwood) lets a single V6 transaction carry both an Orchard bundle and an Ironwood bundle, each with its own Halo2 proof, but the count-based cap did not change and no per-transaction cost cap is applied before proof dispatch. Because mempool and block proof verification share one unprioritized verification queue, a peer sending cheap-to-produce transactions bearing canonically-sized but invalid proofs occupies that queue, so block verification waits behind the attacker's transactions and the node falls behind the tip while the load continues.

This is the same expensive-verification-before-cheap-rejection pattern as GHSA-84j3-rw4c-gqmj, on the shielded proof path rather than the transparent script path, and it shares the Halo2 batch verifier implicated in GHSA-g7c4-2w6c-cr3r. It differs from GHSA-84j3 at the point that made that finding High: the script FFI there ran inline on the async workers and froze the runtime, whereas here proof verification runs on the Rayon pool and the async runtime stays responsive; the impact is a block-verification stall through a shared verification queue, not runtime starvation.

## Details

Verified on v6.2.0.

A V6 transaction carrying Orchard and Ironwood bundles with canonically-sized, zero-filled Halo2 proofs passes each earlier check before proof verification runs:

- Wire deserialization accepts canonically-sized proofs.
- Structural and network-rule checks pass for a well-formed V6 transaction (the Ironwood flag and proof-size rules at `zebra-consensus/src/transaction.rs:586-643` check size and flags, not proof validity).
- Mempool admission is governed only by count-based caps: `MAX_INBOUND_CONCURRENCY = 500` and `MAX_INBOUND_CONCURRENCY_PER_PEER = 5` (`zebrad/src/components/mempool/downloads.rs:106,116`), and the too-many-queued rejections (`downloads.rs:349,366`) are by count. No per-transaction shielded-cost gate applies on this path.
- The anchor and nullifier checks run concurrently with proof verification; with real chain anchors they pass.
- `verify_v6_transaction` (`transaction.rs:1078-1104`) then verifies the shielded bundles: a Sapling Groth16 proof if present, and via `verify_orchard_v6_bundle` both the Orchard bundle and the Ironwood bundle (`:1102-1103`). So one V6 transaction queues two Halo2 proofs plus any Sapling proof.

The Halo2 batch verifier (`zebra-consensus/src/primitives/halo2.rs:236-246`) is a `Fallback` over a `Batch` that flushes at `MAX_BATCH_LATENCY` (100 ms, `primitives.rs:18`) or at the batch action limit. An invalid proof fails the batch, and the `Fallback` re-verifies every item in that batch individually (the slow path). Block-transaction and mempool-transaction verification share this one verifier with no prioritization, so a sustained mempool flood delays block verification.

Before NU6.3, one mempool transaction carried at most one expensive Halo2 proof, so the per-peer cap of 5 bounded concurrent Halo2 verifications per peer. NU6.3 doubled the proofs a transaction can carry without changing the cap, and the cap counts transactions rather than proofs, so the intended bound no longer holds.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-2p4c-3q4q-p463_
