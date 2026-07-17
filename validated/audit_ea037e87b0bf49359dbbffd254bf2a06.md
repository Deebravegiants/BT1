The code evidence is clear. Let me verify the exact validation path and the `proposed_split` accessor.

### Title
Child `ChunkExtra` Inherits Parent `proposed_split` After Shard Split, Causing Permanent `InvalidChunkHeaderShardSplit` on First Child Chunk - (`chain/chain/src/resharding/manager.rs`)

### Summary

`process_memtrie_resharding_storage_update` creates child `ChunkExtra` by cloning the parent and only overwriting `state_root` and `congestion_info`. The `proposed_split` field is never cleared. When the parent's last chunk had `proposed_split = Some(TrieSplit{...})`, every child `ChunkExtra` inherits that value. The first child chunk produced in epoch N+2 computes `proposed_split = None` (because `compute_proposed_split` returns `None` for non-epoch-boundary blocks). `validate_chunk_with_chunk_extra_and_receipts_root` then compares `prev_chunk_extra.proposed_split() = Some(...)` against `chunk_header.proposed_split() = None` and returns `InvalidChunkHeaderShardSplit`, permanently rejecting every valid first child chunk.

### Finding Description

**Step 1 — Parent `ChunkExtra` gets `proposed_split = Some(...)`**

Near the end of epoch N, `compute_proposed_split` is called during chunk application. When the shard exceeds the memory threshold and `is_next_block_possibly_last_in_epoch` returns `true`, it returns `Some(TrieSplit{...})`. This value is stored in the parent's `ChunkExtra.proposed_split`. [1](#0-0) [2](#0-1) 

**Step 2 — Child `ChunkExtra` is created by clone, `proposed_split` is not reset**

At the epoch N/N+1 boundary, `process_memtrie_resharding_storage_update` creates child `ChunkExtra` by cloning the parent and only updating two fields:

```rust
let mut child_chunk_extra = ChunkExtra::clone(&parent_chunk_extra);  // line 258
*child_chunk_extra.state_root_mut() = trie_changes.new_root;         // line 259
*child_chunk_extra.congestion_info_mut() = child_congestion_info;    // line 260
// proposed_split is NEVER reset to None
``` [3](#0-2) 

The TODO comment at line 255 explicitly acknowledges this: "set all fields of `ChunkExtra`." The architecture wiki also records this as TODO item 10: "The resharding manager doesn't set all `ChunkExtra` fields (notably the new `proposed_split` field)." [4](#0-3) 

**Step 3 — First child chunk produces `proposed_split = None`**

In epoch N+2, the first child chunk is produced. `compute_proposed_split` is called and returns `None` because `is_next_block_possibly_last_in_epoch` returns `false` for the first block of the epoch (it is nowhere near the epoch boundary). The chunk header is signed with `proposed_split = None`. [5](#0-4) 

**Step 4 — Validation rejects the chunk**

`validate_chunk_with_chunk_extra_and_receipts_root` compares the stored child `ChunkExtra.proposed_split()` (which is `Some(TrieSplit{...})`) against the incoming chunk header's `proposed_split()` (which is `None`). They differ, so it returns `InvalidChunkHeaderShardSplit`:

```rust
if prev_chunk_extra.proposed_split() != chunk_header.proposed_split() {
    return Err(Error::InvalidChunkHeaderShardSplit(...));
}
``` [6](#0-5) 

This check is reached both during stateless chunk validation (state witness path) and during direct chunk validation when a node has the `ChunkExtra` on disk. [7](#0-6) 

### Impact Explanation

Every node that processed the epoch N/N+1 boundary stores the same child `ChunkExtra` with `proposed_split = Some(...)`. Every valid first child chunk produced by any chunk producer will have `proposed_split = None`. All nodes will reject it with `InvalidChunkHeaderShardSplit`. The child shard cannot produce its first chunk, causing **permanent liveness failure** for the child shard. The chain cannot make progress on that shard. This is a High-severity consensus/liveness impact.

The wiki itself acknowledges the consequence: "allowing back-to-back reshardings is unsafe because a freshly-created child shard would inherit `proposed_split` from the parent's final chunk while its own first chunk freshly computes `proposed_split = None`, triggering `InvalidChunkHeaderShardSplit`." The cooldown (`min_epochs_between_resharding > 0`) prevents a *second* resharding from being proposed, but does **not** clear the inherited `proposed_split` from the child `ChunkExtra` — the root cause is unaddressed. [8](#0-7) 

### Likelihood Explanation

This triggers automatically on the first shard split under `ProtocolFeature::DynamicResharding`. No special attacker action is required beyond the protocol executing a split. Any shard that crosses the memory threshold and gets split will hit this bug deterministically. The `proposed_split` field is set on the last few blocks of the epoch (wherever `is_next_block_possibly_last_in_epoch` returns `true`), so the parent `ChunkExtra` will almost always carry a non-`None` `proposed_split` at the epoch boundary.

### Recommendation

In `process_memtrie_resharding_storage_update`, after cloning the parent `ChunkExtra`, explicitly reset `proposed_split` to `None` on the child:

```rust
let mut child_chunk_extra = ChunkExtra::clone(&parent_chunk_extra);
*child_chunk_extra.state_root_mut() = trie_changes.new_root;
*child_chunk_extra.congestion_info_mut() = child_congestion_info;
// Add:
if let ChunkExtra::V5(ref mut v5) = child_chunk_extra {
    v5.proposed_split = None;
}
```

Or add a `proposed_split_mut()` accessor and use it. The existing TODO comment at line 255 already flags this location. [9](#0-8) 

### Proof of Concept

```rust
// Construct a parent ChunkExtraV5 with proposed_split = Some(TrieSplit{...})
let parent_extra = ChunkExtra::new(
    &state_root,
    outcome_root,
    vec![],
    Gas::ZERO, Gas::ZERO, Balance::ZERO,
    Some(CongestionInfo::default()),
    BandwidthRequests::empty(),
    Some(TrieSplit::new("boundary.near".parse().unwrap(), 100, 100)),
);

// Simulate what process_memtrie_resharding_storage_update does
let mut child_extra = ChunkExtra::clone(&parent_extra);
*child_extra.state_root_mut() = child_state_root;
*child_extra.congestion_info_mut() = child_congestion_info;

// Assert: child proposed_split should be None, but it is Some(...)
assert_eq!(child_extra.proposed_split(), None);  // FAILS: returns Some(TrieSplit{...})

// validate_chunk_with_chunk_extra_and_receipts_root would then compare:
//   prev_chunk_extra.proposed_split() = Some(TrieSplit{...})
//   chunk_header.proposed_split()     = None   (first child chunk, not near epoch boundary)
// => InvalidChunkHeaderShardSplit
``` [10](#0-9)

### Citations

**File:** chain/chain/src/runtime/mod.rs (L284-292)
```rust
        let proposed_split = self.compute_proposed_split(
            &trie,
            shard_id,
            &epoch_id,
            current_protocol_version,
            &epoch_config,
            block_height,
            prev_block_hash,
        )?;
```

**File:** chain/chain/src/runtime/mod.rs (L599-601)
```rust
        if !self.epoch_manager.is_next_block_possibly_last_in_epoch(height, prev_block_hash)? {
            return Ok(None);
        }
```

**File:** core/primitives/src/types.rs (L879-900)
```rust
    /// V4 -> V5: add proposed_split (dynamic resharding)
    #[derive(Debug, PartialEq, BorshSerialize, BorshDeserialize, Clone, Eq, serde::Serialize)]
    pub struct ChunkExtraV5 {
        /// Post state root after applying give chunk.
        pub state_root: StateRoot,
        /// Root of merklizing results of receipts (transactions) execution.
        pub outcome_root: CryptoHash,
        /// Validator proposals produced by given chunk.
        pub validator_proposals: Vec<ValidatorStake>,
        /// Actually how much gas were used.
        pub gas_used: Gas,
        /// Gas limit, allows to increase or decrease limit based on expected time vs real time for computing the chunk.
        pub gas_limit: Gas,
        /// Total balance burnt after processing the current chunk.
        pub balance_burnt: Balance,
        /// Congestion info about this shard after the chunk was applied.
        congestion_info: CongestionInfo,
        /// Requests for bandwidth to send receipts to other shards.
        pub bandwidth_requests: BandwidthRequests,
        /// Proposed split of this shard (dynamic resharding).
        pub proposed_split: Option<TrieSplit>,
    }
```

**File:** core/primitives/src/types.rs (L1066-1071)
```rust
        pub fn proposed_split(&self) -> Option<&TrieSplit> {
            match self {
                Self::V1(_) | Self::V2(_) | Self::V3(_) | Self::V4(_) => None,
                ChunkExtra::V5(v5) => v5.proposed_split.as_ref(),
            }
        }
```

**File:** chain/chain/src/resharding/manager.rs (L255-266)
```rust
            // TODO(resharding): set all fields of `ChunkExtra`. Consider stronger
            // typing. Clarify where it should happen when `State` and
            // `FlatState` update is implemented.
            let mut child_chunk_extra = ChunkExtra::clone(&parent_chunk_extra);
            *child_chunk_extra.state_root_mut() = trie_changes.new_root;
            *child_chunk_extra.congestion_info_mut() = child_congestion_info;

            chain_store_update.save_chunk_extra(
                block_hash,
                &new_shard_uid,
                child_chunk_extra.into(),
            );
```

**File:** docs/architecture/how/dynamic_resharding.md (L98-98)
```markdown
   - Checks the resharding cooldown (`can_reshard()` -- verifies `epoch_height - last_resharding >= min_epochs_between_resharding`). `min_epochs_between_resharding` must be `> 0`: allowing back-to-back reshardings is unsafe because a freshly-created child shard would inherit `proposed_split` from the parent's final chunk while its own first chunk freshly computes `proposed_split = None`, triggering `InvalidChunkHeaderShardSplit`.
```

**File:** docs/architecture/how/dynamic_resharding.md (L282-282)
```markdown
10. **`chain/chain/src/resharding/manager.rs:249`** -- The resharding manager doesn't set all `ChunkExtra` fields (notably the new `proposed_split` field).
```

**File:** chain/chain/src/validate.rs (L176-185)
```rust
    if prev_chunk_extra.proposed_split() != chunk_header.proposed_split() {
        DYNAMIC_RESHARDING_VALIDATION_FAILURES.with_label_values(&["chunk_header"]).inc();
        return Err(Error::InvalidChunkHeaderShardSplit(format!(
            "header has {:?}, expected {:?} (prev block hash: {:?} height created: {:?})",
            chunk_header.proposed_split(),
            prev_chunk_extra.proposed_split(),
            chunk_header.prev_block_hash(),
            chunk_header.height_created(),
        )));
    }
```

**File:** chain/client/src/stateless_validation/chunk_validation_actor.rs (L437-474)
```rust
        if let Ok(prev_chunk_extra) = self.chain_store.get_chunk_extra(&prev_block_hash, &shard_uid)
        {
            match validate_chunk_with_chunk_extra_and_roots(
                &self.chain_store,
                self.epoch_manager.as_ref(),
                &prev_block_hash,
                &prev_chunk_extra,
                last_header.height_included(),
                &chunk_header,
                state_witness.new_transactions(),
                self.rs.as_ref(),
            ) {
                Ok(()) => {
                    send_chunk_endorsement_to_block_producers(
                        &chunk_header,
                        self.epoch_manager.as_ref(),
                        signer.as_ref(),
                        &self.network_adapter,
                    );
                    return Ok(());
                }
                Err(err) => {
                    tracing::error!(
                        target: "chunk_validation",
                        ?err,
                        ?chunk_producer_name,
                        ?chunk_production_key,
                        "failed to validate chunk using existing chunk extra",
                    );
                    CHUNK_WITNESS_VALIDATION_FAILED_TOTAL
                        .with_label_values(&[
                            shard_id.to_string().as_str(),
                            err.prometheus_label_value(),
                        ])
                        .inc();
                    return Err(err);
                }
            }
```
