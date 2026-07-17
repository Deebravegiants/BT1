### Title
TOCTOU Race: Concurrent RPC Transaction Submission After Pool Reshard Strands Transactions in Orphaned Shard Pool — (`chain/chunks/src/client.rs`, `chain/client/src/rpc_handler.rs`)

---

### Summary

A concrete, developer-acknowledged TOCTOU race exists between `ShardedTransactionPool::reshard()` (called under the pool mutex in `Client::on_block_accepted_with_optional_chunk_produce`) and concurrent `RpcHandlerActor::process_tx_internal` calls. The `shard_uid` is computed from the old epoch's shard layout **outside** the pool mutex, then the lock is acquired and the transaction is inserted using the now-stale `shard_uid`. After resharding, no chunk producer will ever drain that old-layout pool entry, so the transaction is silently stranded despite returning `ProcessTxResponse::ValidTx`.

---

### Finding Description

**Step 1 — `shard_uid` computed outside the lock (stale epoch)**

In `process_tx_internal`, the shard layout and `shard_uid` are derived from `head.last_block_hash` before the pool mutex is acquired: [1](#0-0) [2](#0-1) 

The pool lock is only acquired much later: [3](#0-2) 

**Step 2 — `reshard()` runs under the lock, drains old pools, inserts into new**

In `on_block_accepted_with_optional_chunk_produce`, at the epoch boundary, the pool is locked and `reshard()` is called: [4](#0-3) 

`reshard()` iterates and drains all old-shard-uid pools, then re-inserts every transaction under the new shard layout: [5](#0-4) 

After `reshard()` completes, the old `ShardUId` entries remain in `tx_pools` as empty `TransactionPool` objects (the HashMap entries are not removed, only drained).

**Step 3 — Concurrent RPC insert uses stale `shard_uid`**

After `reshard()` releases the lock, `process_tx_internal` acquires it and calls:

```rust
pool.insert_transaction(shard_uid, validated_tx)  // shard_uid is from old layout
```

`pool_for_shard` uses `entry().or_insert_with()`: [6](#0-5) 

This either finds the existing (now-empty) old-layout pool entry or creates a fresh one. Either way, the transaction is inserted into a pool keyed by an old `ShardUId` that no chunk producer in the new epoch will ever call `get_pool_iterator` on.

**Step 4 — Developer-acknowledged, unmitigated**

The code contains an explicit TODO acknowledging this exact gap: [7](#0-6) 

---

### Impact Explanation

A transaction submitted via the public RPC at the epoch-boundary resharding moment is:
- Fully validated (signature, nonce, balance, access key)
- Admitted with `ProcessTxResponse::ValidTx`
- Inserted into an orphaned `ShardUId` pool that no chunk producer will ever drain
- Never included in any block

The user receives a success response but the transaction is silently lost. This violates the mempool admission invariant: every admitted transaction must be routable to a pool that will be drained by the correct chunk producer.

---

### Likelihood Explanation

- Resharding events are rare but real (they occur at planned epoch boundaries when the shard layout changes).
- `RpcHandlerActor` is explicitly a **multithreaded actor** (`handler_threads` configurable), running concurrently with the single-threaded `ClientActor`.
- The race window is the gap between `shard_uid` computation (line 216) and pool lock acquisition (line 279) in `process_tx_internal` — this spans multiple DB reads (`get_chunk_extra`, `can_verify_and_charge_tx`), making the window non-trivial.
- An unprivileged user needs only to submit a transaction via the standard RPC (`broadcast_tx_async` / `send_tx`) at the epoch boundary. No special privileges required.

---

### Recommendation

Compute `shard_uid` **inside** the pool lock, or re-derive it from the current (post-reshard) shard layout at the point of insertion. Alternatively, after acquiring the pool lock, validate that the `shard_uid` version matches the current shard layout version and reject/reroute if it does not. The TODO at line 1890–1891 should be resolved before the next resharding event.

---

### Proof of Concept

```
T=0  Client: on_block_accepted(epoch_boundary_block)
T=1  RpcHandler: head = chain_store.head()  // sees epoch_boundary_block
T=2  RpcHandler: epoch_id = get_epoch_id_from_prev_block(head)  // OLD epoch
T=3  RpcHandler: shard_layout = get_shard_layout(old_epoch_id)  // OLD layout
T=4  RpcHandler: shard_uid = old_layout.account_id_to_shard_uid(signer)  // OLD uid
T=5  Client: pool.lock() -> reshard(old_layout, new_layout) -> pool.unlock()
     // old pools drained, new pools populated
T=6  RpcHandler: pool.lock()
T=7  RpcHandler: pool.insert_transaction(OLD_shard_uid, validated_tx)
     // inserted into orphaned old-layout pool entry
T=8  RpcHandler: returns ProcessTxResponse::ValidTx
     // transaction is stranded; no chunk producer will drain OLD_shard_uid
```

### Citations

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

**File:** chain/client/src/client.rs (L1890-1891)
```rust
            // TODO make sure transactions don't get added for the old shard
            // layout after the pool resharding
```

**File:** chain/client/src/client.rs (L1900-1901)
```rust
                            let mut guarded_pool = self.chunk_producer.sharded_tx_pool.lock();
                            guarded_pool.reshard(&old_shard_layout, &new_shard_layout);
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

**File:** chain/chunks/src/client.rs (L142-156)
```rust
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
```
