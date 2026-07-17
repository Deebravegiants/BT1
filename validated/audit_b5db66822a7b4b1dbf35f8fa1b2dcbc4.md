The code path is concrete and traceable. Let me lay out the findings.

## Key Code: `StateSync::run` stale-hash check [1](#0-0) 

```rust
if highest_height > block_header.height() + chain.epoch_length + STALE_SYNC_HASH_THRESHOLD {
    return Ok(StateSyncResult::StaleSyncHash);
}
```

`highest_height` is a plain `u64` passed in from the caller — it is not a quorum value, not a median, and not validated against any chain proof. It is derived from peer-advertised heights.

## Propagation to `EpochSyncDataReset`

In `handler.rs`, `StateSyncResult::StaleSyncHash` maps directly to `SyncHandlerRequest::EpochSyncDataReset` with no additional guard: [2](#0-1) 

## The Invariant Violation

The check at line 283 uses a single aggregated-max `highest_height` derived from `highest_height_peers`. A single peer advertising `highest_block_height = sync_hash_height + epoch_length + STALE_SYNC_HASH_THRESHOLD + 1` is sufficient to satisfy the condition. There is no:
- Quorum requirement (e.g., majority of peers must agree)
- Proof-of-work or block header verification of the claimed height
- Rate-limiting or cooldown before triggering the destructive reset

The threshold comment itself acknowledges this is meant to guard against genuine network advancement, not peer-claimed heights: [3](#0-2) 

## Impact Assessment

The impact is **not** ordinary resource waste or DoS. `EpochSyncDataReset` causes the node to wipe its database and restart. If the attack is repeated on each restart (the attacker simply stays connected and keeps advertising the inflated height), the node permanently fails to complete state sync and never recovers canonical state. This matches the stated scope: "fail to recover canonical state."

---

### Title
Single-peer inflated height triggers unconditional `StaleSyncHash` → DB wipe during state sync — (`chain/client/src/sync/state/mod.rs`)

### Summary
`StateSync::run` compares `highest_height` (derived from the maximum of peer-advertised heights, with no quorum) against `block_header.height() + epoch_length + STALE_SYNC_HASH_THRESHOLD`. A single malicious peer advertising a sufficiently large `highest_block_height` satisfies this condition and causes the node to return `StateSyncResult::StaleSyncHash`, which unconditionally maps to `SyncHandlerRequest::EpochSyncDataReset` — wiping the node's DB and restarting it.

### Finding Description
The stale-sync-hash detection at [1](#0-0)  uses a single `u64` (`highest_height`) that is the maximum height reported by any peer in `highest_height_peers`. No quorum, no block header proof, and no rate-limit guard the transition to `StaleSyncHash`. The handler at [2](#0-1)  converts this result directly into `EpochSyncDataReset` with no additional check.

### Impact Explanation
A node in `SyncStatus::StateSync` with a valid `sync_hash` can be forced to wipe its DB and restart by any single peer that claims `highest_block_height >= sync_hash_height + epoch_length + STALE_SYNC_HASH_THRESHOLD + 1`. If the attacker reconnects after each restart and repeats the advertisement, the node never completes state sync and permanently fails to recover canonical state.

### Likelihood Explanation
Any unprivileged peer on the NEAR P2P network can advertise an arbitrary `highest_block_height` in its peer info. No stake, validator key, or special privilege is required. The attack requires only a persistent P2P connection.

### Recommendation
Replace the single-peer-max `highest_height` check with a quorum-based threshold (e.g., the median or a supermajority of connected peers must report a height exceeding the threshold). Alternatively, require that the claimed height be backed by a verifiable block header before triggering the destructive reset. At minimum, add a rate-limit or confirmation window (e.g., the condition must hold for N consecutive ticks across M distinct peers) before executing `EpochSyncDataReset`.

### Proof of Concept
In a test-loop test: start a node in `SyncStatus::StateSync` with a known `sync_hash` at height `H`. Inject a `NetworkInfo` with `highest_height_peers` containing exactly one peer with `highest_block_height = H + epoch_length + STALE_SYNC_HASH_THRESHOLD + 1`. Call `StateSync::run`. Assert that `StateSyncResult::StaleSyncHash` is returned and `EpochSyncDataReset` is emitted, despite the sync hash being current and valid. The existing test infrastructure in [4](#0-3)  already exercises this path and can be adapted.

### Citations

**File:** chain/client/src/sync/state/mod.rs (L46-65)
```rust
/// Number of blocks past epoch_length that triggers stale sync hash detection.
///
/// During state sync, if the network's highest height exceeds the sync hash
/// block's height + epoch_length + this threshold, the sync hash is considered
/// stale and the node triggers a data reset + restart.
///
/// Must be large enough to account for epoch stretching due to missing blocks
/// and finality delays. Epoch boundaries require `last_finalized_height + 3
/// >= estimated_next_epoch_start`, so with sparse block production, epochs
/// can extend beyond epoch_length. A 100-block threshold is safe because a
/// false positive would require 100+ blocks without finality — a catastrophic
/// consensus failure, not normal missing blocks.
///
/// Under `test_features`, the threshold is lowered to 5 so tests with
/// epoch_length=10 can trigger stale sync hash detection without needing
/// hundreds of blocks.
#[cfg(not(feature = "test_features"))]
pub const STALE_SYNC_HASH_THRESHOLD: u64 = 100;
#[cfg(feature = "test_features")]
pub const STALE_SYNC_HASH_THRESHOLD: u64 = 5;
```

**File:** chain/client/src/sync/state/mod.rs (L283-291)
```rust
        if highest_height > block_header.height() + chain.epoch_length + STALE_SYNC_HASH_THRESHOLD {
            tracing::warn!(
                target: "sync",
                ?block_header,
                highest_height,
                "stale sync hash detected, triggering data reset"
            );
            return Ok(StateSyncResult::StaleSyncHash);
        }
```

**File:** chain/client/src/sync/handler.rs (L150-152)
```rust
                    StateSyncResult::StaleSyncHash => {
                        return Ok(Some(SyncHandlerRequest::EpochSyncDataReset));
                    }
```

**File:** test-loop-tests/src/tests/sync/far_horizon.rs (L1-10)
```rust
//! Far-horizon sync tests.
//!
//! These test the full V2 pipeline for nodes that are many epochs behind:
//!   EpochSync → HeaderSync → StateSync → BlockSync → NoSync
//!
//! The node must do epoch sync to bootstrap, then headers to learn the chain,
//! then state sync to get shard state, then block sync to catch up.
//!
//! Note: shard shuffling is intentionally NOT enabled in these tests. Far-horizon
//! tests bootstrap a fresh observer node via epoch sync — the node is not a
```
