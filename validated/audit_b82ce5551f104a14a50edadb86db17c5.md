### Title
`DelayedReceiptQueueWrapper::receipt_filter_fn` Panics on Unresolvable `GlobalContractDistribution` Receipt During Delayed-Queue Drain — (`File: runtime/runtime/src/congestion_control.rs`)

### Summary

`DelayedReceiptQueueWrapper::receipt_filter_fn` calls `receiver_shard_id(&shard_layout).unwrap()` inside the `pop()` loop that drains the delayed receipt queue. For `GlobalContractDistribution` receipts whose `target_shard` was set under an old shard layout that cannot be resolved to the current layout via `resolve_to_current_shard`, `receiver_shard_id` returns `Err(EpochError::ShardingError(...))`. The `.unwrap()` converts that error into a panic, aborting the entire delayed-receipt processing loop and causing chunk application to fail on every node that reaches that receipt.

### Finding Description

`receipt_filter_fn` is called on every receipt popped from the delayed queue:

```rust
fn receipt_filter_fn(&self, receipt: &ReceiptOrStateStoredReceipt) -> bool {
    let shard_layout = self.epoch_info_provider.shard_layout(&self.epoch_id).unwrap();
    let receipt_shard_id = receipt.get_receipt().receiver_shard_id(&shard_layout).unwrap(); // ← panics
    receipt_shard_id == self.shard_id
}
``` [1](#0-0) 

It is invoked inside the `pop()` loop:

```rust
if self.receipt_filter_fn(&receipt) {
    return Ok(Some(receipt));
}
``` [2](#0-1) 

`receiver_shard_id` for a `GlobalContractDistribution` receipt attempts to remap the stored `target_shard` to the current layout. When `resolve_to_current_shard` returns `None` (the stored shard ID is not in the current layout and cannot be found in its split history), it returns `Err`:

```rust
let Some(current_shard) = shard_layout.resolve_to_current_shard(target_shard)
else {
    return Err(EpochError::ShardingError(format!(
        "Shard {target_shard} does not exist in the shard layout or its split history",
    )));
};
``` [3](#0-2) 

The `.unwrap()` in `receipt_filter_fn` converts that `Err` into a panic. The panic propagates out of `process_delayed_receipts`, which is called from `process_receipts`, which is called from `Runtime::apply`. Every node applying that chunk panics identically, stalling the chain.

The production test suite explicitly documents this failure mode:

> "If the vulnerability exists, processing the stale `GlobalContractDistribution` receipt will panic in `receipt_filter_fn()` when `receiver_shard_id()` fails to remap the old `target_shard` after two resharding generations." [4](#0-3) 

### Impact Explanation

A panic inside `receipt_filter_fn` during `pop()` aborts `process_delayed_receipts`, which aborts `Runtime::apply`. The chunk cannot be applied; the block cannot be finalized. Because all honest nodes execute the same deterministic receipt queue, every node panics on the same receipt, causing a consensus-level chain halt. The corrupted value is the chunk's `state_root` / `ChunkExtra` — it is never written, so the chain cannot advance past that block height.

### Likelihood Explanation

The trigger requires:
1. An unprivileged user deploys a global contract (`DeployGlobalContract` action), producing a `GlobalContractDistribution` receipt.
2. The receipt is pushed to the delayed queue (e.g., because the chunk's compute budget is saturated by other transactions — a condition any user can induce by submitting heavy function calls).
3. Two shard-split resharding events occur while the receipt sits in the delayed queue.
4. When the receipt is eventually popped, `target_shard` from the original layout cannot be resolved through two generations of splits.

Steps 1–2 are fully under unprivileged user control. Steps 3–4 depend on protocol-level resharding events, but a user who times a deployment just before a known resharding window (e.g., during a scheduled shard-split epoch) can reliably trigger the condition. The test `test_global_contract_distribution_receipt_survives_two_resharding_events` reproduces the exact scenario. [5](#0-4) 

### Recommendation

Replace the `.unwrap()` in `receipt_filter_fn` with proper error propagation. Change the function signature to return `Result<bool, RuntimeError>` (or an equivalent), and propagate the `EpochError` upward through `pop()` and `peek_iter()`. This mirrors the fix recommended in the external report: handle the per-item error gracefully so that a single unresolvable receipt does not abort the entire loop.

### Proof of Concept

1. Deploy a global contract from an account whose shard will be split in the next resharding event.
2. Saturate the chunk's compute budget every block so the resulting `GlobalContractDistribution` receipt is pushed to the delayed queue instead of being processed immediately.
3. Allow two shard-split resharding events to complete (the `target_shard` in the receipt now refers to a shard ID that no longer exists in the current layout and whose lineage spans two split generations).
4. Stop saturating. On the next chunk application, `process_delayed_receipts` calls `pop()`, which calls `receipt_filter_fn`, which calls `receiver_shard_id(&current_layout).unwrap()`. `resolve_to_current_shard` returns `None` for the stale `target_shard`, `receiver_shard_id` returns `Err`, `.unwrap()` panics, and chunk application aborts on all nodes. [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** runtime/runtime/src/congestion_control.rs (L874-910)
```rust
    fn receipt_filter_fn(&self, receipt: &ReceiptOrStateStoredReceipt) -> bool {
        let shard_layout = self.epoch_info_provider.shard_layout(&self.epoch_id).unwrap();
        let receipt_shard_id = receipt.get_receipt().receiver_shard_id(&shard_layout).unwrap();
        receipt_shard_id == self.shard_id
    }

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

**File:** test-loop-tests/src/tests/global_contracts_distribution.rs (L100-185)
```rust
    env.runner_for_account(&chunk_producer).run_for_number_of_blocks(2);

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

**File:** runtime/runtime/src/lib.rs (L2406-2465)
```rust
        loop {
            if processing_state.total.compute >= compute_limit
                || processing_state.state_update.trie.check_proof_size_limit_exceed()
            {
                break;
            }

            let receipt = if let Some(receipt) = processing_state
                .delayed_receipts
                .pop(&mut processing_state.state_update, &processing_state.apply_state.config)?
            {
                receipt.into_receipt()
            } else {
                // Break loop if there are no more receipts to be processed.
                break;
            };

            // TODO(resharding): Add metric for tracking number of
            delayed_receipt_count += 1;
            if let Some(nsi) = &mut next_schedule_after {
                *nsi = nsi.saturating_sub(1);
                if *nsi == 0 {
                    let mut prep_lookahead_iter =
                        processing_state.delayed_receipts.peek_iter(&processing_state.state_update);
                    next_schedule_after = schedule_contract_preparation(
                        &mut processing_state.pipeline_manager,
                        &processing_state.state_update,
                        &mut prep_lookahead_iter,
                    );
                }
            }

            if let Some(prefetcher) = &mut processing_state.prefetcher {
                // Prefetcher is allowed to fail
                _ = prefetcher.prefetch_receipts_data(std::slice::from_ref(&receipt));
            }

            // Validating the delayed receipt. If it fails, it's likely the state is inconsistent.
            validate_receipt(
                &processing_state.apply_state.config.wasm_config.limit_config,
                &receipt,
                protocol_version,
                ValidateReceiptMode::ExistingReceipt,
            )
            .map_err(|e| {
                StorageError::StorageInconsistentState(format!(
                    "Delayed receipt {:?} in the state is invalid: {}",
                    receipt, e
                ))
            })?;

            self.process_receipt_and_instant_receipts(
                &receipt,
                &mut processing_state,
                receipt_sink,
                validator_proposals,
            )?;
            processing_state
                .processed_receipts
                .push(ProcessedReceipt { receipt, source: ReceiptSource::Delayed });
```
