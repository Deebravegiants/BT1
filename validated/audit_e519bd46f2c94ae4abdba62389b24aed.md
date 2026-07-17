Looking at the exact code path in detail to verify the claim.

### Title
SPICE Resharding Epoch Mismatch in `process_tx_internal` Bypasses Congestion Control for New Child Shards - (`chain/client/src/rpc_handler.rs`)

### Summary

In `process_tx_internal`, the current epoch's `shard_layout` is passed to `spice_shard_congestion_info` alongside a `certified_header` that may be from the **previous epoch** (with a different `ShardLayout`). When resharding has occurred and certification is lagging, the new child shard's `ShardUId` (built from the new layout version) does not exist in the old epoch's `ChunkExtra` store, and the new child `shard_id` does not exist in the old epoch's `execution_results`. Both lookups return `None`, causing `spice_shard_congestion_info` to return `None`. `validate_tx` then skips the congestion gate entirely, admitting transactions to a congested new child shard that should be rejected.

### Finding Description

**Step 1 — Precondition is reachable in production.**

The test `test_spice_certified_results_across_resharding` explicitly asserts and confirms that after resharding with a certification delay, the first block of the new epoch has its last certified block in the previous epoch with a different shard layout. The epoch-gating mechanism (`is_next_block_in_next_epoch`) allows the consensus chain to be at most one epoch ahead of the certified epoch, so this cross-epoch lag is a normal operating condition. [1](#0-0) 

**Step 2 — The shard layout mismatch in `process_tx_internal`.**

`shard_layout` is fetched from the **current epoch** (post-resharding, layout version N+1). `spice_certified_header` is the last certified block header, which may be from the **previous epoch** (pre-resharding, layout version N). `receiver_shard` is computed from the current epoch's layout. These are then passed together to `spice_shard_congestion_info`: [2](#0-1) 

**Step 3 — `spice_shard_congestion_info` returns `None` for the new child shard.**

Inside `spice_shard_congestion_info`, `ShardUId::from_shard_id_and_layout(shard_id, shard_layout)` builds a `ShardUId` with the **new layout version** (N+1). The call to `chunk_store.get_chunk_extra(block_header.hash(), &shard_uid)` fails because the old epoch's block only has `ChunkExtra` entries keyed by old-layout `ShardUId`s (version N). The fallback `get_execution_result_from_store(chain_store, block_header.hash(), shard_id)` also returns `None` because the new child `shard_id` did not exist in the old epoch's execution results. The function returns `None`. [3](#0-2) 

**Step 4 — `validate_tx` skips the congestion gate.**

`validate_tx` only checks congestion when `receiver_congestion_info` is `Some`. With `None`, the entire `if let Some(congestion_info)` branch is skipped and the transaction is admitted unconditionally. [4](#0-3) 

**Step 5 — The bypass propagates to chunk production.**

`spice_block_congestion_info` (used by the chunk producer) correctly uses `epoch_manager.get_shard_layout(block_header.epoch_id())` — the certified header's own epoch's layout — so it iterates over the **old** shard IDs and never inserts an entry for the new child shard. When `congestion_control_accepts_transaction` looks up the new child shard in the resulting `BlockCongestionInfo`, it finds `None` and returns `Ok(true)` (accept), bypassing the gate at chunk production time as well. [5](#0-4) [6](#0-5) 

Note the asymmetry: `spice_block_congestion_info` passes the certified header's own epoch's layout (consistent), while `process_tx_internal` passes the **current** epoch's layout (inconsistent). The RPC path is the only caller with the mismatch.

### Impact Explanation

Any unprivileged user can submit a transaction whose `receiver_id` maps to a new child shard (created by resharding) while that shard is congested and the certified header is still in the pre-resharding epoch. The transaction bypasses `ShardCongested`/`ShardStuck` rejection at both the RPC admission gate and the chunk producer's transaction filter. The transaction is admitted to the mempool, included in a chunk, and converted to a receipt — producing a different receipt set than the congestion control invariant requires.

### Likelihood Explanation

The conditions are all normal operating states:
- SPICE is enabled (protocol feature flag)
- Resharding occurs (a planned network operation)
- Certification lags by at least one block into the new epoch (the epoch-gating mechanism explicitly allows up to one epoch of lag, and the test confirms this lag occurs with even a delay of 2 blocks)

An attacker needs only to submit a transaction to a receiver account on the new child shard during this window. No validator or operator privileges are required.

### Recommendation

In `process_tx_internal`, replace the current-epoch `shard_layout` with the certified header's own epoch's shard layout when calling `spice_shard_congestion_info`, mirroring what `spice_block_congestion_info` already does correctly:

```rust
// Instead of:
spice_shard_congestion_info(&self.chain_store, &shard_layout, certified_header.as_ref(), receiver_shard)

// Use the certified header's own epoch layout:
let certified_shard_layout = self.epoch_manager.get_shard_layout(certified_header.epoch_id())?;
let certified_receiver_shard = certified_shard_layout.account_id_to_shard_id(receiver_id);
spice_shard_congestion_info(&self.chain_store, &certified_shard_layout, certified_header.as_ref(), certified_receiver_shard)
```

If the receiver's account maps to a new child shard that has no entry in the certified epoch's layout (i.e., the shard was just created), the function will still return `None`. A secondary fix should treat `None` from `spice_shard_congestion_info` during a cross-epoch resharding transition as "unknown/potentially congested" rather than "uncongested," or fall back to the parent shard's congestion info.

### Proof of Concept

Extend `test_spice_certified_results_across_resharding` in `test-loop-tests/src/tests/spice/resharding.rs`:

1. After resharding, while the certified header is still in the old epoch, artificially congest the new child shard (by filling its delayed receipts gas via a burst of cross-shard calls).
2. Submit a transaction whose `receiver_id` maps to the new child shard.
3. Call `process_tx` and assert the response is `ValidTx` (bypassed) rather than `InvalidTx(ShardCongested { .. })`.
4. Verify that `spice_shard_congestion_info` called with the current epoch's layout and the old certified header returns `None` for the new child shard's `shard_id`. [7](#0-6) [8](#0-7)

### Citations

**File:** test-loop-tests/src/tests/spice/resharding.rs (L76-87)
```rust
    // Assert that the first block of the resharded epoch has its last certified
    // block in the previous epoch with a different number of shards.
    let node = env.validator();
    let chain_store = &node.client().chain.chain_store;
    let header = chain_store.get_block_header_by_height(new_epoch_start).unwrap();
    let last_certified = get_last_certified_block_header(chain_store, header.hash()).unwrap();
    let certified_shard_layout = epoch_manager.get_shard_layout(last_certified.epoch_id()).unwrap();
    assert_ne!(
        epoch_manager.get_shard_layout(header.epoch_id()).unwrap(),
        certified_shard_layout,
        "expected the first block of the resharded epoch to have its last certified block in the previous epoch with different shard count"
    );
```

**File:** chain/client/src/rpc_handler.rs (L175-201)
```rust
        let epoch_id = self.epoch_manager.get_epoch_id_from_prev_block(&head.last_block_hash)?;
        let protocol_version = self.epoch_manager.get_epoch_protocol_version(&epoch_id)?;
        let shard_layout = self.epoch_manager.get_shard_layout(&epoch_id)?;
        let receiver_shard =
            shard_layout.account_id_to_shard_id(signed_tx.transaction.receiver_id());
        // TODO(spice): get_last_certified_block_header does multiple DB reads
        // (loading uncertified chunks + block headers). Cache the last certified
        // block header for the current head, or store the last-certified hash in
        // chain state so this is O(1).
        let spice_certified_header = if ProtocolFeature::Spice.enabled(protocol_version) {
            Some(get_last_certified_block_header(&self.chain_store, &head.last_block_hash)?)
        } else {
            None
        };

        let receiver_congestion_info = if let Some(certified_header) = &spice_certified_header {
            // Receiver-shard congestion from the last certified block's executed
            // ChunkExtras, to reject transactions to a congested shard.
            spice_shard_congestion_info(
                &self.chain_store,
                &shard_layout,
                certified_header.as_ref(),
                receiver_shard,
            )
        } else {
            cur_block.block_congestion_info().get(&receiver_shard).copied()
        };
```

**File:** chain/chain/src/spice/chunk_application.rs (L243-258)
```rust
pub fn spice_block_congestion_info(
    chain_store: &ChainStoreAdapter,
    epoch_manager: &dyn EpochManagerAdapter,
    block_header: &BlockHeader,
) -> Result<BlockCongestionInfo, Error> {
    let shard_layout = epoch_manager.get_shard_layout(block_header.epoch_id())?;
    let mut result = BTreeMap::new();
    for shard_id in shard_layout.shard_ids() {
        if let Some(extended) =
            spice_shard_congestion_info(chain_store, &shard_layout, block_header, shard_id)
        {
            result.insert(shard_id, extended);
        }
    }
    Ok(BlockCongestionInfo::new(result))
}
```

**File:** chain/chain/src/spice/chunk_application.rs (L267-284)
```rust
pub fn spice_shard_congestion_info(
    chain_store: &ChainStoreAdapter,
    shard_layout: &ShardLayout,
    block_header: &BlockHeader,
    shard_id: ShardId,
) -> Option<ExtendedCongestionInfo> {
    let shard_uid = ShardUId::from_shard_id_and_layout(shard_id, shard_layout);
    let chunk_store = chain_store.chunk_store();
    let congestion_info =
        if let Ok(chunk_extra) = chunk_store.get_chunk_extra(block_header.hash(), &shard_uid) {
            chunk_extra.congestion_info()
        } else {
            get_execution_result_from_store(chain_store, block_header.hash(), shard_id)?
                .chunk_extra
                .congestion_info()
        };
    Some(ExtendedCongestionInfo::new(congestion_info, 0))
}
```

**File:** chain/chain/src/runtime/mod.rs (L724-747)
```rust
        if let Some(congestion_info) = receiver_congestion_info {
            let congestion_control = CongestionControl::new(
                runtime_config.congestion_control_config,
                congestion_info.congestion_info,
                congestion_info.missed_chunks_count,
            );
            if let ShardAcceptsTransactions::No(reason) =
                congestion_control.shard_accepts_transactions()
            {
                let shard_id =
                    shard_layout.account_id_to_shard_id(signed_tx.transaction.receiver_id()).into();
                let err = match reason {
                    RejectTransactionReason::IncomingCongestion { congestion_level }
                    | RejectTransactionReason::OutgoingCongestion { congestion_level }
                    | RejectTransactionReason::MemoryCongestion { congestion_level } => {
                        InvalidTxError::ShardCongested { shard_id, congestion_level }
                    }
                    RejectTransactionReason::MissedChunks { missed_chunks } => {
                        InvalidTxError::ShardStuck { shard_id, missed_chunks }
                    }
                };
                return Err((err, signed_tx));
            }
        }
```

**File:** chain/chain/src/runtime/mod.rs (L1701-1713)
```rust
fn congestion_control_accepts_transaction(
    epoch_manager: &dyn EpochManagerAdapter,
    runtime_config: &RuntimeConfig,
    epoch_id: &EpochId,
    prev_block: &PrepareTransactionsBlockContext,
    validated_tx: &ValidatedTransaction,
) -> Result<bool, Error> {
    let receiver_id = validated_tx.receiver_id();
    let receiving_shard = account_id_to_shard_id(epoch_manager, receiver_id, &epoch_id)?;
    let congestion_info = prev_block.congestion_info.get(&receiving_shard);
    let Some(congestion_info) = congestion_info else {
        return Ok(true);
    };
```
