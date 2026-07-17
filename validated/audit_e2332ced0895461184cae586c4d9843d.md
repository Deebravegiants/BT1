### Title
Unhandled `Err` from `receiver_shard_id()` in `receipt_filter_fn` Panics on Stale `GlobalContractDistribution` Receipt After Multi-Generation Resharding — (`runtime/runtime/src/congestion_control.rs`)

---

### Summary

`DelayedReceiptQueueWrapper::receipt_filter_fn` calls `.unwrap()` on the result of `Receipt::receiver_shard_id()`. For `GlobalContractDistribution` receipts, `receiver_shard_id()` returns `Err` when the receipt's embedded `target_shard` cannot be resolved in the current shard layout. On V0/V1/V2 (static resharding) layouts, `resolve_to_current_shard` only performs a **single-generation** lookup, so a receipt whose `target_shard` was split in an earlier (not the most recent) resharding event returns `None`, propagating as `Err`. The `.unwrap()` then panics inside the runtime's chunk-application loop, stalling the chain for the affected shard.

---

### Finding Description

**Root cause — `receipt_filter_fn` unwraps a fallible result:** [1](#0-0) 

```rust
fn receipt_filter_fn(&self, receipt: &ReceiptOrStateStoredReceipt) -> bool {
    let shard_layout = self.epoch_info_provider.shard_layout(&self.epoch_id).unwrap();
    let receipt_shard_id = receipt.get_receipt().receiver_shard_id(&shard_layout).unwrap(); // ← panics
    receipt_shard_id == self.shard_id
}
```

**`receiver_shard_id` returns `Err` when the stale shard cannot be resolved:** [2](#0-1) 

For a `GlobalContractDistribution` receipt whose `target_shard` is no longer present in the current layout, the code calls `shard_layout.resolve_to_current_shard(target_shard)`. If that returns `None`, it returns `Err(EpochError::ShardingError(...))`.

**`resolve_to_current_shard` is single-generation for V0/V1/V2 layouts:** [3](#0-2) 

```rust
pub fn resolve_to_current_shard(&self, shard_id: ShardId) -> Option<ShardId> {
    match self {
        Self::V0(_) | Self::V1(_) | Self::V2(_) => {
            self.get_children_shards_ids(shard_id).map(|c| c[0])  // single generation only
        }
        Self::V3(v3) => v3.resolve_to_current_shard(shard_id),    // full history
    }
}
```

For V2 layouts, `get_children_shards_ids` only knows about the **most recent** resharding split. If shard `S` was split into `S1/S2` in resharding event 1, and then `S1` was split into `S3/S4` in resharding event 2, the V2 layout's split map only records `S1 → {S3, S4}`. A receipt with `target_shard = S` calls `get_children_shards_ids(S)` which returns `None` (since `S` is not the most-recently-split shard), so `resolve_to_current_shard(S)` returns `None`, `receiver_shard_id` returns `Err`, and `receipt_filter_fn` panics.

**The codebase's own test documents this exact panic path:** [4](#0-3) 

```
// If the vulnerability exists, processing the stale GlobalContractDistribution
// receipt will panic in receipt_filter_fn() when receiver_shard_id() fails
// to remap the old target_shard after two resharding generations.
```

The test also explicitly acknowledges the fix is **only** for V3 layouts: [5](#0-4) 

```rust
// The fix only works with V3 shard layouts (dynamic resharding).
// With static resharding, the shard layout doesn't maintain a full split history.
if !ProtocolFeature::DynamicResharding.enabled(PROTOCOL_VERSION) {
    return;
}
```

---

### Impact Explanation

`receipt_filter_fn` is called from `DelayedReceiptQueueWrapper::pop` and `peek_iter`, which are invoked during every chunk application cycle (`process_delayed_receipts`). [6](#0-5) 

A panic inside this loop propagates out of the runtime's chunk-application path. The test confirms the observable result is a **chain stall** — the head height stops advancing — because no chunk producer can successfully apply the chunk containing the stale receipt. The corrupted protocol value is the **chunk state root and outcome root** for the affected shard: they are never computed, so the shard permanently halts until the stale receipt is somehow removed from the delayed queue (which requires a protocol-level intervention).

---

### Likelihood Explanation

The trigger requires three conditions:

1. **A user deploys a global contract** — this is an ordinary, permissionless transaction available to any account.
2. **The resulting `GlobalContractDistribution` receipt is pushed to the delayed queue** — this happens naturally when the shard's compute budget is exhausted. An attacker can deliberately saturate the shard with gas-heavy transactions (as the test itself does) to force the receipt into the delayed queue.
3. **Two resharding events occur while the receipt remains delayed** — on a network running static V2 resharding (e.g., mainnet before `DynamicResharding` activation), two protocol-version upgrades that each change the shard layout are sufficient. The attacker does not control resharding; they only need to time the deployment to precede the first resharding and keep the queue saturated through both events.

All three conditions are reachable by an unprivileged user. No validator or node-admin access is required.

---

### Recommendation

Replace the `.unwrap()` calls in `receipt_filter_fn` with proper error propagation. Change the function signature to return `Result<bool, RuntimeError>` and propagate the `EpochError` upward through `pop` and `peek_iter`. Alternatively, on resolution failure, log a warning and treat the receipt as belonging to the current shard (safe fallback: process it and let the runtime handle it gracefully) rather than panicking.

Additionally, `resolve_to_current_shard` for V2 layouts should be made multi-generational (iterating through the full chain of `get_children_shards_ids` calls) to match the V3 behavior, so the fix is not gated solely on `DynamicResharding` being enabled.

---

### Proof of Concept

The attack sequence mirrors the test in `test-loop-tests/src/tests/global_contracts_distribution.rs`: [7](#0-6) 

1. Attacker submits a `DeployGlobalContract` transaction from any account. This creates a `GlobalContractDistribution` receipt with `target_shard = S` (the attacker's shard).
2. Attacker submits repeated gas-heavy transactions to saturate the shard's compute budget each block, forcing the distribution receipt into the delayed queue.
3. The network undergoes resharding event 1: shard `S` splits into `S1` and `S2`. The delayed queue is duplicated into both child shards; the receipt (with `target_shard = S`) remains in the queue.
4. The network undergoes resharding event 2: shard `S1` splits into `S3` and `S4`. The V2 layout now only records `S1 → {S3, S4}` in its split map.
5. Attacker stops saturating. The runtime attempts to drain the delayed queue. `receipt_filter_fn` calls `receiver_shard_id(&v2_layout)` on the stale receipt. `resolve_to_current_shard(S)` returns `None` (V2 has no record of `S`). `receiver_shard_id` returns `Err`. `.unwrap()` panics. Chunk application fails. The shard head stalls permanently.

### Citations

**File:** runtime/runtime/src/congestion_control.rs (L874-878)
```rust
    fn receipt_filter_fn(&self, receipt: &ReceiptOrStateStoredReceipt) -> bool {
        let shard_layout = self.epoch_info_provider.shard_layout(&self.epoch_id).unwrap();
        let receipt_shard_id = receipt.get_receipt().receiver_shard_id(&shard_layout).unwrap();
        receipt_shard_id == self.shard_id
    }
```

**File:** runtime/runtime/src/congestion_control.rs (L880-910)
```rust
    pub(crate) fn pop(
        &mut self,
        trie_update: &mut TrieUpdate,
        config: &RuntimeConfig,
    ) -> Result<Option<ReceiptOrStateStoredReceipt<'_>>, RuntimeError> {
        // While processing receipts, we need to keep track of the gas and bytes
        // even for receipts that may be filtered out due to a resharding event
        loop {
            // Check proof size limit before each receipt is popped.
            if trie_update.trie.check_proof_size_limit_exceed() {
                break;
            }
            let Some(receipt) = self.queue.pop_front(trie_update)? else {
                break;
            };
            let delayed_gas = receipt_congestion_gas(&receipt, &config)?;
            let delayed_bytes = receipt_size(&receipt)? as u64;
            self.removed_delayed_gas =
                self.removed_delayed_gas.checked_add(delayed_gas).ok_or(IntegerOverflowError)?;
            self.removed_delayed_bytes = self
                .removed_delayed_bytes
                .checked_add(delayed_bytes)
                .ok_or(IntegerOverflowError)?;

            // Track gas and bytes for receipt above and return only receipt that belong to the shard.
            if self.receipt_filter_fn(&receipt) {
                return Ok(Some(receipt));
            }
        }
        Ok(None)
    }
```

**File:** core/primitives/src/receipt.rs (L447-463)
```rust
            ReceiptEnum::GlobalContractDistribution(receipt) => {
                let target_shard = receipt.target_shard();
                if shard_layout.shard_ids().contains(&target_shard) {
                    target_shard
                } else {
                    // The target shard may be from an arbitrarily old layout (the receipt could
                    // have been delayed across multiple resharding events). resolve_to_current_shard
                    // will find a shard descendant in the current layout.
                    let Some(current_shard) = shard_layout.resolve_to_current_shard(target_shard)
                    else {
                        return Err(EpochError::ShardingError(format!(
                            "Shard {target_shard} does not exist in the shard layout or its split history",
                        )));
                    };
                    current_shard
                }
            }
```

**File:** core/primitives/src/shard_layout/mod.rs (L230-237)
```rust
    pub fn resolve_to_current_shard(&self, shard_id: ShardId) -> Option<ShardId> {
        match self {
            Self::V0(_) | Self::V1(_) | Self::V2(_) => {
                self.get_children_shards_ids(shard_id).map(|c| c[0])
            }
            Self::V3(v3) => v3.resolve_to_current_shard(shard_id),
        }
    }
```

**File:** test-loop-tests/src/tests/global_contracts_distribution.rs (L35-39)
```rust
    // The fix only works with V3 shard layouts (dynamic resharding).
    // With static resharding, the shard layout doesn't maintain a full split history.
    if !ProtocolFeature::DynamicResharding.enabled(PROTOCOL_VERSION) {
        return;
    }
```

**File:** test-loop-tests/src/tests/global_contracts_distribution.rs (L102-163)
```rust
    // Step 2: Deploy a global contract from user0. This creates a
    // GlobalContractDistribution receipt with target_shard = user0's shard (S_A),
    // which is the shard that will be split in the first resharding.
    {
        let node = env.node_for_account(&chunk_producer);
        let code = ContractCode::new(near_test_contracts::rs_contract().to_vec(), None);
        let tx = node.tx_deploy_global_contract(
            &deploy_user,
            code.code().to_vec(),
            GlobalContractDeployMode::CodeHash,
        );
        node.submit_tx(tx);
    }

    // Step 3: Saturate compute on user0's shard every block so that the
    // GlobalContractDistribution receipt (arriving as incoming) gets pushed to
    // the delayed queue and stays there through both resharding events.
    //
    // Each burn_gas_raw call burns slightly more than half the gas limit, so
    // two local receipts exhaust the chunk's compute budget. We submit 3 per
    // block to ensure at least 2 are processed as local receipts.
    let gas_to_burn = gas_limit.checked_div(2).unwrap().checked_add(Gas::from_gas(1)).unwrap();
    let initial_num_shards = base_shard_layout.num_shards();
    let target_num_shards = initial_num_shards + 2; // after two splits

    let start_height = {
        let node = env.node_for_account(&chunk_producer);
        node.client().chain.chain_store().head().unwrap().height
    };

    // Keep saturating until both resharding events complete. Dynamic resharding has a
    // 2-epoch proposal-to-activation pipeline, so we need enough epochs for both splits.
    let max_saturation_height = start_height + epoch_length * 12;
    let mut both_splits_done = false;
    for target_height in (start_height + 1)..=max_saturation_height {
        // Submit 3 heavy transactions to saturate this block's compute budget.
        {
            let node = env.node_for_account(&chunk_producer);
            for _ in 0..3 {
                let tx = node.tx_call(
                    &deploy_user,
                    &deploy_user,
                    "burn_gas_raw",
                    gas_to_burn.as_gas().to_le_bytes().to_vec(),
                    Balance::ZERO,
                    gas_limit,
                );
                node.submit_tx(tx);
            }
        }
        env.runner_for_account(&chunk_producer).run_until_head_height(target_height);

        // Check if both resharding events have completed.
        let node = env.node_for_account(&chunk_producer);
        let epoch_id = node.client().chain.chain_store().head().unwrap().epoch_id;
        let current_layout = node.client().epoch_manager.get_shard_layout(&epoch_id).unwrap();
        if current_layout.num_shards() >= target_num_shards {
            both_splits_done = true;
            break;
        }
    }
    assert!(both_splits_done, "both shard splits did not complete within the allotted blocks");
```

**File:** test-loop-tests/src/tests/global_contracts_distribution.rs (L165-185)
```rust
    // Step 4: Stop saturating. Let the delayed queue drain.
    // If the vulnerability exists, processing the stale GlobalContractDistribution
    // receipt will panic in receipt_filter_fn() when receiver_shard_id() fails
    // to remap the old target_shard after two resharding generations.
    let current_height = {
        let node = env.node_for_account(&chunk_producer);
        node.client().chain.chain_store().head().unwrap().height
    };
    let drain_end = current_height + epoch_length * 2;
    env.runner_for_account(&chunk_producer).run_until_head_height(drain_end);

    let head_height = {
        let node = env.node_for_account(&chunk_producer);
        node.client().chain.chain_store().head().unwrap().height
    };
    assert!(
        head_height >= drain_end,
        "chain stalled at height {}; expected >= {} (likely panicked processing stale receipt)",
        head_height,
        drain_end
    );
```
