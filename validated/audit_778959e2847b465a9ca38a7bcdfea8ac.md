### Title
`PromiseYield` Receipts Excluded from `CongestionInfo.receipt_bytes` Allows Attacker to Understate Memory Congestion - (`runtime/runtime/src/congestion_control.rs`)

### Summary

`CongestionInfoV1.receipt_bytes` is documented to track the size of all receipts stored in state, including "yielded" receipts. However, `PromiseYield` receipts stored via `set_promise_yield_receipt()` are never added to `receipt_bytes`. An unprivileged user can deploy a contract that calls `promise_yield_create` repeatedly, accumulating large `PromiseYieldReceipt` trie entries that are invisible to the congestion control system. This causes `memory_congestion` to be systematically understated, causing other shards to forward receipts to the affected shard at a higher rate than the protocol intends, worsening actual congestion for all users.

### Finding Description

`CongestionInfoV1` documents its `receipt_bytes` field as:

> "Size of borsh serialized receipts stored in state because they were delayed, buffered, postponed, or **yielded**." [1](#0-0) 

However, `compute_receipt_congestion_gas()` explicitly returns `Gas::ZERO` for `PromiseYield` receipts: [2](#0-1) 

And `bootstrap_congestion_info()` only iterates over the delayed receipt queue and outgoing buffers — it never iterates over `TrieKey::PromiseYieldReceipt` entries: [3](#0-2) 

When a `PromiseYield` receipt is processed, it is stored in state via `set_promise_yield_receipt()` with no corresponding `add_receipt_bytes()` call: [4](#0-3) 

Similarly, when a `PromiseYield` receipt is removed (on resume or timeout), there is no `remove_receipt_bytes()` call: [5](#0-4) 

The `DelayedReceiptQueueWrapper.push()` correctly calls `compute_receipt_congestion_gas()` and tracks both gas and bytes for delayed receipts: [6](#0-5) 

But there is no equivalent wrapper for `PromiseYield` receipt storage.

### Impact Explanation

`memory_congestion` is computed as `receipt_bytes / max_congestion_memory_consumption`: [7](#0-6) 

`memory_congestion` feeds into the overall `congestion_level()`, which determines how much gas other shards are allowed to forward to this shard: [8](#0-7) 

Because `PromiseYield` receipts are not counted in `receipt_bytes`, the `CongestionInfo` embedded in the chunk header — which is the authoritative value all validators and other shards use — understates actual memory usage. Other shards therefore forward receipts at a higher rate than they should, worsening actual congestion for all users of the affected shard. The corrupted value is `CongestionInfo.receipt_bytes` in the chunk header, which propagates to all shards via `BlockCongestionInfo`. [9](#0-8) 

### Likelihood Explanation

Any unprivileged user can deploy a contract that calls `promise_yield_create` in a loop. Each call stores a `PromiseYieldReceipt` trie entry (hundreds of bytes each) that is invisible to `receipt_bytes`. With `yield_timeout_length_in_blocks = 200`, an attacker must continuously submit transactions to maintain the inflated state. The gas cost is non-trivial but affordable for a sustained griefing attack. The attack is fully reachable via public RPC transactions.

### Recommendation

When storing a `PromiseYield` receipt in `process_receipt()`, call `congestion_info.add_receipt_bytes(compute_receipt_size(receipt)?)` and subtract the same amount when removing it on resume or timeout. Update `bootstrap_congestion_info()` to also iterate over `TrieKey::PromiseYieldReceipt` entries and include their sizes in `receipt_bytes`. Alternatively, if the design decision is to intentionally exclude `PromiseYield` receipts from memory congestion accounting, update the `CongestionInfoV1.receipt_bytes` documentation to remove "yielded" from the list of tracked receipt types.

### Proof of Concept

1. Deploy a contract with a method that calls `promise_yield_create` N times (up to gas limit).
2. Submit transactions calling this method repeatedly across many blocks.
3. Each call stores a `PromiseYieldReceipt` entry in the trie under `TrieKey::PromiseYieldReceipt`.
4. Observe via RPC (`view_chunk`) that `congestion_info.receipt_bytes` does not increase despite growing trie storage.
5. Observe that other shards continue forwarding receipts at the uncongested rate even as actual memory usage grows.
6. The `memory_congestion` level remains at 0 regardless of how many `PromiseYield` receipts are stored, because `receipt_bytes` is never incremented for them. [10](#0-9) [11](#0-10)

### Citations

**File:** core/primitives/src/congestion_info.rs (L44-54)
```rust
    pub fn congestion_level(&self) -> f64 {
        let incoming_congestion = self.incoming_congestion();
        let outgoing_congestion = self.outgoing_congestion();
        let memory_congestion = self.memory_congestion();
        let missed_chunks_congestion = self.missed_chunks_congestion();

        incoming_congestion
            .max(outgoing_congestion)
            .max(memory_congestion)
            .max(missed_chunks_congestion)
    }
```

**File:** core/primitives/src/congestion_info.rs (L345-347)
```rust
    pub fn memory_congestion(&self, config: &CongestionControlConfig) -> f64 {
        clamped_f64_fraction(self.receipt_bytes() as u128, config.max_congestion_memory_consumption)
    }
```

**File:** core/primitives/src/congestion_info.rs (L387-395)
```rust
/// The block congestion info contains the congestion info for all shards in the
/// block extended with the missed chunks count.
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct BlockCongestionInfo {
    /// The per shard congestion info. It's important that the data structure is
    /// deterministic because the allowed shard id selection depends on the
    /// order of shard ids in this map. Ideally it should also be sorted by shard id.
    shards_congestion_info: BTreeMap<ShardId, ExtendedCongestionInfo>,
}
```

**File:** core/primitives/src/congestion_info.rs (L460-470)
```rust
pub struct CongestionInfoV1 {
    /// Sum of gas in currently delayed receipts.
    pub delayed_receipts_gas: u128,
    /// Sum of gas in currently buffered receipts.
    pub buffered_receipts_gas: u128,
    /// Size of borsh serialized receipts stored in state because they
    /// were delayed, buffered, postponed, or yielded.
    pub receipt_bytes: u64,
    /// If fully congested, only this shard can forward receipts.
    pub allowed_shard: u16,
}
```

**File:** runtime/runtime/src/congestion_control.rs (L678-714)
```rust
pub(crate) fn compute_receipt_congestion_gas(
    receipt: &Receipt,
    config: &RuntimeConfig,
) -> Result<Gas, IntegerOverflowError> {
    match receipt.versioned_receipt() {
        VersionedReceiptEnum::Action(action_receipt) => {
            // account for gas guaranteed to be used for executing the receipts
            action_receipt_congestion_gas(receipt, config, action_receipt.into())
        }
        VersionedReceiptEnum::Data(_data_receipt) => {
            // Data receipts themselves don't cost gas to execute, their cost is
            // burnt at creation. What we should count, is the gas of the
            // postponed action receipt. But looking that up would require
            // reading the postponed receipt from the trie.
            // Thus, the congestion control MVP does not account for data
            // receipts or postponed receipts.
            Ok(Gas::ZERO)
        }
        VersionedReceiptEnum::PromiseYield(_) => {
            // The congestion control MVP does not account for yielding a
            // promise. Yielded promises are confined to a single account, hence
            // they never cross the shard boundaries. This makes it irrelevant
            // for the congestion MVP, which only counts gas in the outgoing
            // buffers and delayed receipts queue.
            Ok(Gas::ZERO)
        }
        VersionedReceiptEnum::PromiseResume(_) => {
            // The congestion control MVP does not account for resuming a promise.
            // Unlike `PromiseYield`, it is possible that a promise-resume ends
            // up in the delayed receipts queue.
            // But similar to a data receipt, it would be difficult to find the cost
            // of it without expensive state lookups.
            Ok(Gas::ZERO)
        }
        VersionedReceiptEnum::GlobalContractDistribution(_) => Ok(Gas::ZERO),
    }
}
```

**File:** runtime/runtime/src/congestion_control.rs (L743-789)
```rust
pub fn bootstrap_congestion_info(
    trie: &dyn near_store::TrieAccess,
    config: &RuntimeConfig,
    shard_id: ShardId,
) -> Result<CongestionInfo, StorageError> {
    let mut receipt_bytes: u64 = 0;
    let mut delayed_receipts_gas: u128 = 0;
    let mut buffered_receipts_gas: u128 = 0;

    let delayed_receipt_queue = &DelayedReceiptQueue::load(trie)?;
    for receipt_result in delayed_receipt_queue.iter(trie, true) {
        let receipt = receipt_result?;
        let gas =
            receipt_congestion_gas(&receipt, config).map_err(int_overflow_to_storage_err)?.as_gas();
        delayed_receipts_gas = safe_add_gas_to_u128(delayed_receipts_gas, Gas::from_gas(gas))
            .map_err(int_overflow_to_storage_err)?;

        let memory = receipt_size(&receipt).map_err(int_overflow_to_storage_err)? as u64;
        receipt_bytes = receipt_bytes.checked_add(memory).ok_or_else(overflow_storage_err)?;
    }

    let mut outgoing_buffers = ShardsOutgoingReceiptBuffer::load(trie)?;
    for shard in outgoing_buffers.shards() {
        for receipt_result in outgoing_buffers.to_shard(shard).iter(trie, true) {
            let receipt = receipt_result?;
            let gas = receipt_congestion_gas(&receipt, config)
                .map_err(int_overflow_to_storage_err)?
                .as_gas();
            buffered_receipts_gas = safe_add_gas_to_u128(buffered_receipts_gas, Gas::from_gas(gas))
                .map_err(int_overflow_to_storage_err)?;
            let memory = receipt_size(&receipt).map_err(int_overflow_to_storage_err)? as u64;
            receipt_bytes = receipt_bytes.checked_add(memory).ok_or_else(overflow_storage_err)?;
        }
    }

    Ok(CongestionInfo::V1(CongestionInfoV1 {
        delayed_receipts_gas: delayed_receipts_gas as u128,
        buffered_receipts_gas: buffered_receipts_gas as u128,
        receipt_bytes,
        // For the first chunk, set this to the own id.
        // This allows bootstrapping without knowing all other shards.
        // It is also irrelevant, since the bootstrapped value is only used at
        // the start of applying a chunk on this shard. Other shards will only
        // see and act on the first congestion info after that.
        allowed_shard: shard_id.into(),
    }))
}
```

**File:** runtime/runtime/src/congestion_control.rs (L838-866)
```rust
    pub(crate) fn push(
        &mut self,
        trie_update: &mut TrieUpdate,
        receipt: &Receipt,
        apply_state: &ApplyState,
    ) -> Result<(), RuntimeError> {
        let config = &apply_state.config;

        let gas = compute_receipt_congestion_gas(&receipt, &config)?;
        let size = compute_receipt_size(&receipt)? as u64;

        // TODO It would be great to have this method take owned Receipt and
        // get rid of the Cow from the Receipt and StateStoredReceipt.
        let receipt = match config.use_state_stored_receipt {
            true => {
                let metadata =
                    StateStoredReceiptMetadata { congestion_gas: gas, congestion_size: size };
                let receipt = StateStoredReceipt::new_borrowed(receipt, metadata);
                ReceiptOrStateStoredReceipt::StateStoredReceipt(receipt)
            }
            false => ReceiptOrStateStoredReceipt::Receipt(Cow::Borrowed(receipt)),
        };

        self.new_delayed_gas = self.new_delayed_gas.checked_add(gas).ok_or(IntegerOverflowError)?;
        self.new_delayed_bytes =
            self.new_delayed_bytes.checked_add(size).ok_or(IntegerOverflowError)?;
        self.queue.push_back(trie_update, &receipt)?;
        Ok(())
    }
```

**File:** runtime/runtime/src/lib.rs (L1416-1420)
```rust
            VersionedReceiptEnum::PromiseYield(_) => {
                // Received a new PromiseYield receipt. We simply store it and await
                // the corresponding PromiseResume receipt.
                set_promise_yield_receipt(state_update, receipt);
            }
```

**File:** runtime/runtime/src/lib.rs (L1438-1442)
```rust
                    // Remove the receipt from the state
                    remove_promise_yield_receipt(state_update, account_id, data_receipt.data_id);

                    // Clear the PromiseYield status
                    remove_promise_yield_status(state_update, account_id, data_receipt.data_id);
```

**File:** core/store/src/utils/mod.rs (L182-194)
```rust
pub fn set_promise_yield_receipt(state_update: &mut TrieUpdate, receipt: &Receipt) {
    match receipt.versioned_receipt() {
        VersionedReceiptEnum::PromiseYield(action_receipt) => {
            assert!(action_receipt.input_data_ids().len() == 1);
            let key = TrieKey::PromiseYieldReceipt {
                receiver_id: receipt.receiver_id().clone(),
                data_id: action_receipt.input_data_ids()[0],
            };
            set(state_update, key, receipt);
        }
        _ => unreachable!("Expected PromiseYield receipt"),
    }
}
```
