### Title
Shard-Layout Version Mismatch in `spice_shard_congestion_info` Bypasses Congestion Gate for New Child Shards at Resharding Boundary — (`chain/client/src/rpc_handler.rs`, `chain/chain/src/spice/chunk_application.rs`)

---

### Summary

Under `ProtocolFeature::Spice` with an active resharding boundary, `process_tx_internal` passes the **current epoch's** `shard_layout` to `spice_shard_congestion_info` while the `certified_header` is from the **previous epoch** (a natural consequence of endorsement lag). This causes both DB lookups inside `spice_shard_congestion_info` to fail for any new child shard, returning `None`. `validate_tx` only enforces the congestion gate when `receiver_congestion_info` is `Some`, so the gate is silently bypassed. The same gap exists in the chunk producer's `prepare_transactions` path, meaning the transaction is also included in a chunk. An unprivileged user can exploit this to inject transactions into a fully-congested new child shard.

---

### Finding Description

**Step 1 — RPC entry point and layout mismatch**

In `process_tx_internal`, the current epoch's shard layout is fetched and used to resolve the receiver shard: [1](#0-0) 

The SPICE certified header is then fetched independently: [2](#0-1) 

`get_last_certified_block_header` walks back from the current head to find the oldest block with all chunks certified. With endorsement lag (by design in SPICE), this header is routinely in the **previous epoch** — a different shard layout version. [3](#0-2) 

**Step 2 — Both DB lookups fail inside `spice_shard_congestion_info`**

`spice_shard_congestion_info` is called with the **new epoch's** `shard_layout` but the **old epoch's** `block_header`: [4](#0-3) 

Inside the function, `ShardUId` is constructed from the new epoch's layout (version N+1): [5](#0-4) 

- **Primary lookup** (`get_chunk_extra`): The certified block's `ChunkExtra` entries were stored under the **old epoch's** `ShardUId` (version N). Looking them up with a version-N+1 `ShardUId` returns `Err` — the key does not exist.
- **Fallback lookup** (`get_execution_result_from_store`): Keyed by `(block_hash, shard_id)`. The new child `shard_id` did not exist in the old epoch, so no execution result was ever written for it. Returns `None`.

Both paths fail → `spice_shard_congestion_info` returns `None`. [6](#0-5) 

**Step 3 — `validate_tx` skips the congestion check when `receiver_congestion_info` is `None`** [7](#0-6) 

The congestion gate is only enforced when `receiver_congestion_info` is `Some`. With `None`, `validate_transaction` proceeds unconditionally.

**Step 4 — Chunk producer also bypasses the gate**

In `chunk_producer.rs`, `spice_block_congestion_info` is called with the certified header: [8](#0-7) 

`spice_block_congestion_info` uses the **certified header's epoch** shard layout, iterating only over old-epoch shards: [9](#0-8) 

The new child shard is never inserted into the result. Then `congestion_control_accepts_transaction` explicitly returns `Ok(true)` when the receiving shard has no entry: [10](#0-9) 

The transaction is included in the chunk.

---

### Impact Explanation

An unprivileged user submitting a transaction via public RPC to a receiver account that maps to a new child shard (post-resharding) will have that transaction:
1. Admitted at the RPC level (`ProcessTxResponse::ValidTx`) despite the child shard being at congestion level 1.0.
2. Included in a produced chunk by the chunk producer, because the same missing-congestion-info path returns `Ok(true)`.

This bypasses the congestion control mechanism that is supposed to prevent overloading congested shards, worsening congestion and potentially causing cascading backpressure failures across the shard graph. The impact matches the stated scope: "admits invalid transactions... before block inclusion."

---

### Likelihood Explanation

All required conditions are naturally present in a SPICE + resharding deployment:
- **SPICE enabled**: required for the certified-header path to activate.
- **Resharding boundary**: a planned protocol event; the window spans the first several blocks of the new epoch (until the certified header advances past the epoch boundary).
- **Certified header in old epoch**: guaranteed by endorsement lag, which is by design in SPICE.
- **Congested new child shard**: plausible if the parent shard was congested before the split, or if an attacker deliberately congests it first.

The test in `test-loop-tests/src/tests/spice/resharding.rs` already confirms that the first block of a resharded epoch has its certified block in the previous epoch with a different shard count: [11](#0-10) 

---

### Recommendation

In `process_tx_internal`, resolve the receiver shard's congestion info using the **certified header's epoch shard layout**, not the current epoch's layout. Specifically:

1. Fetch the certified header's epoch shard layout: `epoch_manager.get_shard_layout(certified_header.epoch_id())`.
2. Map the current-epoch `receiver_shard` back to its parent shard in the old epoch (using `get_prev_shard_id_from_prev_hash` or equivalent) before calling `spice_shard_congestion_info`.
3. Apply the same fix to `spice_block_congestion_info` in `chunk_producer.rs`: after building congestion info from the certified header's old-epoch shards, map each old-epoch shard's congestion info forward to the new-epoch child shards it covers.

The existing `TODO(spice-resharding)` comments in `build_block_congestion_info` acknowledge this gap: [12](#0-11) 

---

### Proof of Concept

In a test-loop test with SPICE and resharding (mirroring `test_spice_certified_results_across_resharding`):

1. Configure two epochs: old layout (1 shard), new layout (2 child shards).
2. Set `execution_delay = 3` so the certified header lags by 3 blocks.
3. Advance to the first block of the new epoch (certified header is still in old epoch).
4. Congest child shard 1 to level 1.0 by submitting gas-burning transactions (using the existing congestion test harness from `test-loop-tests/src/tests/spice/congestion.rs`).
5. Submit a transaction whose receiver maps to child shard 1 (the congested one).
6. Assert `ProcessTxResponse::ValidTx` — the congestion gate is bypassed.
7. Assert the transaction appears in the next produced chunk for child shard 0 (the signer's shard), confirming end-to-end admission.

### Citations

**File:** chain/client/src/rpc_handler.rs (L175-179)
```rust
        let epoch_id = self.epoch_manager.get_epoch_id_from_prev_block(&head.last_block_hash)?;
        let protocol_version = self.epoch_manager.get_epoch_protocol_version(&epoch_id)?;
        let shard_layout = self.epoch_manager.get_shard_layout(&epoch_id)?;
        let receiver_shard =
            shard_layout.account_id_to_shard_id(signed_tx.transaction.receiver_id());
```

**File:** chain/client/src/rpc_handler.rs (L184-188)
```rust
        let spice_certified_header = if ProtocolFeature::Spice.enabled(protocol_version) {
            Some(get_last_certified_block_header(&self.chain_store, &head.last_block_hash)?)
        } else {
            None
        };
```

**File:** chain/client/src/rpc_handler.rs (L190-201)
```rust
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

**File:** chain/chain/src/spice/core.rs (L715-722)
```rust
pub(crate) fn get_execution_result_from_store(
    chain_store: &ChainStoreAdapter,
    block_hash: &CryptoHash,
    shard_id: ShardId,
) -> Option<Arc<ChunkExecutionResult>> {
    let key = get_execution_results_key(block_hash, shard_id);
    chain_store.store().caching_get_ser(DBCol::execution_results(), &key)
}
```

**File:** chain/chain/src/spice/core.rs (L1048-1066)
```rust
pub fn get_last_certified_block_header(
    chain_store: &ChainStoreAdapter,
    block_hash: &CryptoHash,
) -> Result<Arc<BlockHeader>, Error> {
    let uncertified_chunks = get_uncertified_chunks(chain_store, block_hash)?;
    let oldest_uncertified = find_oldest_uncertified_block_header(chain_store, uncertified_chunks)?;
    if let Some(header) = oldest_uncertified {
        Ok(chain_store.get_block_header(header.prev_hash())?)
    } else {
        // No uncertified-chunks tracking means the block has nothing to
        // certify: genesis, or a pre-spice block at the activation
        // boundary. Both are fully certified by definition.
        let header = chain_store.get_block_header(block_hash)?;
        debug_assert!(
            header.is_genesis() || !header.is_spice(),
            "post-genesis spice blocks should always have uncertified chunks"
        );
        Ok(header)
    }
```

**File:** chain/chain/src/spice/chunk_application.rs (L248-257)
```rust
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
```

**File:** chain/chain/src/spice/chunk_application.rs (L273-283)
```rust
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
```

**File:** chain/chain/src/spice/chunk_application.rs (L326-328)
```rust
    // TODO(spice-resharding): across a resharding boundary both children map to the
    // same parent and inherit its congestion info unsplit. See dynamic_resharding.md.
    for shard_id in shard_layout.shard_ids() {
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

**File:** chain/chain/src/runtime/mod.rs (L1710-1712)
```rust
    let congestion_info = prev_block.congestion_info.get(&receiving_shard);
    let Some(congestion_info) = congestion_info else {
        return Ok(true);
```

**File:** chain/client/src/chunk_producer.rs (L520-529)
```rust
                let congestion_info = spice_block_congestion_info(
                    &self.chain,
                    self.epoch_manager.as_ref(),
                    certified_header.as_ref(),
                )?;
                let prev_block_context = PrepareTransactionsBlockContext::new(
                    prev_block,
                    &*self.epoch_manager,
                    congestion_info,
                )?;
```

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
