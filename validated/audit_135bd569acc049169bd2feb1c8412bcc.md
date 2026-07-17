The race condition is real and the code even acknowledges it with a TODO comment. Let me trace the exact path.

---

### Title
Post-Reshard Old-Layout ShardUId Ghost Entry Causes Silent Transaction Loss — (`chain/client/src/client.rs`, `chain/client/src/rpc_handler.rs`, `chain/chunks/src/client.rs`)

### Summary

A genuine TOCTOU race between `RpcHandlerActor::process_tx_internal` (multithreaded) and `Client::on_block_accepted_with_optional_chunk_produce` (single-threaded ClientActor) allows a transaction submitted via public RPC to be silently inserted into a stale old-layout `ShardUId` pool entry that is never iterated by chunk producers, permanently dropping the transaction from the mempool.

### Finding Description

**Step 1 — RPC handler reads the chain head (old epoch)**

`process_tx_internal` reads `head` from the chain store at the very start: [1](#0-0) 

If `head.last_block_hash` is the pre-boundary block (last block of the old epoch, but `is_next_block_epoch_start` returns `false` for it), then: [2](#0-1) 

`get_epoch_id_from_prev_block` returns the **old epoch ID**, so `shard_layout` is the **old shard layout**, and: [3](#0-2) 

`shard_uid` is an **old-layout `ShardUId`**.

**Step 2 — ClientActor processes the boundary block and reshards the pool**

Concurrently, the ClientActor accepts the epoch-boundary block and calls `reshard()`: [4](#0-3) 

The code even has a TODO acknowledging this exact problem: [5](#0-4) 

`reshard()` drains all old-layout `ShardUId` pools and re-inserts every transaction under new-layout `ShardUId` keys: [6](#0-5) 

After `reshard()` completes, the `tx_pools` HashMap contains only new-layout `ShardUId` keys.

**Step 3 — RPC handler inserts into a ghost old-layout pool entry**

The RPC handler then acquires the pool lock and inserts: [7](#0-6) 

`pool_for_shard` uses `HashMap::entry(...).or_insert_with(...)`, so it silently creates a **brand-new** `TransactionPool` keyed by the old-layout `ShardUId`: [8](#0-7) 

**Step 4 — Transaction is invisible to chunk producers**

Chunk producers call `get_pool_iterator(new_shard_uid)`, which does a direct HashMap lookup: [9](#0-8) 

The transaction is in a pool keyed by an old-layout `ShardUId` that no chunk producer will ever query. It is permanently stranded.

### Impact Explanation

Any transaction submitted via public RPC (`broadcast_tx_async`, `broadcast_tx_commit`, `send_tx`) during the narrow window between:
- the chain store head being updated to the epoch-boundary block, and
- `reshard()` completing

will be silently dropped from the mempool and never included in any chunk. The user receives `ValidTx` (success) but the transaction is never executed. This is a concrete mempool-level impact reachable by any unprivileged user.

### Likelihood Explanation

- The race window is narrow (milliseconds at epoch boundaries with shard layout changes)
- Dynamic resharding is gated behind `ProtocolFeature::DynamicResharding`, so this only triggers when that feature is active
- The `RpcHandlerActor` is explicitly multithreaded (`spawn_multithread_actor`) and runs concurrently with the ClientActor
- The code has an explicit TODO acknowledging this exact problem, confirming the developers are aware of the gap

### Recommendation

After calling `reshard()`, the pool must reject or re-route any subsequent `insert_transaction` call that uses an old-layout `ShardUId`. One approach: store the current `ShardLayout` version inside `ShardedTransactionPool` and validate the `shard_uid.version()` on every `insert_transaction` call, returning an error or re-mapping to the new layout if the version is stale. Alternatively, the RPC handler should re-derive `shard_uid` while holding the pool lock, using the layout version stored in the pool itself.

### Proof of Concept

In a test-loop test:
1. Configure a static resharding epoch boundary (two protocol versions, old and new shard layout).
2. Run until the boundary block is accepted.
3. In a hook that fires immediately after `chain.postprocess_ready_blocks` updates the head (but before `on_block_accepted_with_optional_chunk_produce` acquires the pool lock), inject a `ProcessTxRequest` directly into the `RpcHandlerActor` with a transaction whose signer maps to a shard that is being split.
4. Let the ClientActor complete `reshard()`.
5. Assert that `get_pool_iterator` on every new-layout `ShardUId` returns zero transactions — the transaction is stranded in the ghost old-layout pool entry.
6. Assert that `tx_pools` contains an entry keyed by the old-layout `ShardUId` with exactly one transaction.

### Citations

**File:** chain/client/src/rpc_handler.rs (L157-157)
```rust
        let head = self.chain_store.head()?;
```

**File:** chain/client/src/rpc_handler.rs (L175-177)
```rust
        let epoch_id = self.epoch_manager.get_epoch_id_from_prev_block(&head.last_block_hash)?;
        let protocol_version = self.epoch_manager.get_epoch_protocol_version(&epoch_id)?;
        let shard_layout = self.epoch_manager.get_shard_layout(&epoch_id)?;
```

**File:** chain/client/src/rpc_handler.rs (L216-217)
```rust
        let shard_uid = shard_layout.account_id_to_shard_uid(signed_tx.transaction.signer_id());
        let shard_id = shard_uid.shard_id();
```

**File:** chain/client/src/rpc_handler.rs (L279-280)
```rust
                let mut pool = self.tx_pool.lock();
                match pool.insert_transaction(shard_uid, validated_tx) {
```

**File:** chain/client/src/client.rs (L1888-1908)
```rust
            // If the next block is the first of the next epoch and the shard
            // layout is changing we need to reshard the transaction pool.
            // TODO make sure transactions don't get added for the old shard
            // layout after the pool resharding
            if self.epoch_manager.is_next_block_epoch_start(&block_hash).unwrap_or(false) {
                let new_shard_layout =
                    self.epoch_manager.get_shard_layout_from_prev_block(&block_hash);
                let old_shard_layout =
                    self.epoch_manager.get_shard_layout_from_prev_block(block.header().prev_hash());
                match (old_shard_layout, new_shard_layout) {
                    (Ok(old_shard_layout), Ok(new_shard_layout)) => {
                        if old_shard_layout != new_shard_layout {
                            let mut guarded_pool = self.chunk_producer.sharded_tx_pool.lock();
                            guarded_pool.reshard(&old_shard_layout, &new_shard_layout);
                        }
                    }
                    (old_shard_layout, new_shard_layout) => {
                        tracing::warn!(target: "client", ?old_shard_layout, ?new_shard_layout, "failed to check if shard layout is changing");
                    }
                }
            }
```

**File:** chain/chunks/src/client.rs (L60-62)
```rust
    pub fn get_pool_iterator(&mut self, shard_uid: ShardUId) -> Option<PoolIteratorWrapper<'_>> {
        self.tx_pools.get_mut(&shard_uid).map(|pool| pool.pool_iterator())
    }
```

**File:** chain/chunks/src/client.rs (L91-99)
```rust
    fn pool_for_shard(&mut self, shard_uid: ShardUId) -> &mut TransactionPool {
        self.tx_pools.entry(shard_uid).or_insert_with(|| {
            TransactionPool::new(
                Self::random_seed(&self.rng_seed, shard_uid.shard_id()),
                self.pool_size_limit,
                &shard_uid.to_string(),
            )
        })
    }
```

**File:** chain/chunks/src/client.rs (L131-157)
```rust
    pub fn reshard(&mut self, old_shard_layout: &ShardLayout, new_shard_layout: &ShardLayout) {
        tracing::debug!(
            target: "resharding",
            old_shard_layout_version = old_shard_layout.version(),
            new_shard_layout_version = new_shard_layout.version(),
            "resharding the transaction pool"
        );
        debug_assert!(old_shard_layout != new_shard_layout);

        let mut validated_txs = vec![];

        for old_shard_uid in old_shard_layout.shard_uids() {
            if let Some(mut iter) = self.get_pool_iterator(old_shard_uid) {
                while let Some(group) = iter.next() {
                    while let Some(validated_tx) = group.next() {
                        validated_txs.push(validated_tx);
                    }
                }
            }
        }

        for validated_tx in validated_txs {
            let signer_id = validated_tx.signer_id();
            let new_shard_uid = new_shard_layout.account_id_to_shard_uid(signer_id);
            self.insert_transaction(new_shard_uid, validated_tx);
        }
    }
```
