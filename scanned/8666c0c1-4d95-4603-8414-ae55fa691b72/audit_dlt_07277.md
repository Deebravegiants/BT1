# [?] fix(chain): don't panic on gas overflow in early transaction preparation (#16390)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-09-04
Source: https://github.com/near/nearcore/commit/59308f59a267b8a7563c0a1715e54d77f169e229
Type: security-commit

## Details
fix(chain): don't panic on gas overflow in early transaction preparation (#16390)

Chunk header gas fields are only cross-checked against
`prev_chunk_extra` for the shards a node applies, and the
optimistic-block path sums them across *all* shards before any
block-level check runs. The sum can overflow and the `unwrap` panics.

Early transaction preparation is an optimization, so skip it instead of
crashing.

## Patch
### chain/chain/src/chain.rs
```diff
@@ -3762,24 +3762,33 @@ impl Chain {
         // Assume that next epoch id is the same as the current one. This will not be true on epoch
         // boundaries, but that is ok. On epoch id mismatch the result of early transaction
         // preparation will be ignored.
-        let next_chunk_prepare_context = {
-            // Unwrap is safe here because chunk headers are already verified.
-            let gas_used = chunk_headers.compute_gas_used_checked().unwrap();
-            let gas_limit = chunk_headers.compute_gas_limit_checked().unwrap();
-            PrepareTransactionsBlockContext {
-                next_gas_price: Block::compute_next_gas_price_checked(
+        let Some(next_gas_price) = chunk_headers
+            .compute_gas_used_checked()
+            .zip(chunk_headers.compute_gas_limit_checked())
+            .and_then(|(gas_used, gas_limit)| {
+                Block::compute_next_gas_price_checked(
                     prev_block.header().next_gas_price(),
                     gas_used,
                     gas_limit,
                     self.block_economics_config.gas_price_adjustment_rate(),
                     self.block_economics_config.min_gas_price(),
                     self.block_economics_config.max_gas_price(),
                 )
-                .unwrap(),
-                height: block.height,
-                next_epoch_id: epoch_id,
-                congestion_info: block.congestion_info.clone(),
-            }
+            })
+        else {
+            tracing::debug!(
+                target: "chain",
+                height = block.height,
+                shard_id = %shard_uid.shard_id(),
+                "gas overflow in chunk headers; skipping early transaction preparation"
+            );
+            return None;
+        };
+        let next_chunk_prepare_context = PrepareTransactionsBlockContext {
+            next_gas_price,
+            height: block.height,
+            next_epoch_id: epoch_id,
+            congestion_info: block.congestion_info.clone(),
         };
 
         // Transactions included in the current chunk, they aren't removed from the pool yet and
```

### chain/client/src/chunk_producer.rs
```diff
@@ -29,6 +29,8 @@ use near_primitives::optimistic_block::{CachedShardUpdateKey, OptimisticBlockKey
 use near_primitives::receipt::Receipt;
 use near_primitives::sharding::{ShardChunkHeader, ShardChunkWithEncoding};
 use near_primitives::transaction::SignedTransaction;
+#[cfg(feature = "test_features")]
+use near_primitives::types::Gas;
 use near_primitives::types::chunk_extra::ChunkExtra;
 use near_primitives::types::{BlockHeight, EpochId, ShardId};
 use near_primitives::validator_signer::ValidatorSigner;
@@ -76,6 +78,8 @@ pub struct ChunkProducerAdversarialControls {
     pub produce_mode: Option<AdvProduceChunksMode>,
     pub produce_invalid_chunks: bool,
     pub produce_invalid_tx_in_chunks: bool,
+    /// Forge `prev_gas_used` and `gas_limit` to `Gas::MAX`.
+    pub produce_max_gas_chunk_header: bool,
 }
 
 pub struct ProduceChunkResult {
@@ -132,6 +136,7 @@ impl ChunkProducer {
                 produce_mode: None,
                 produce_invalid_chunks: false,
                 produce_invalid_tx_in_chunks: false,
+                produce_max_gas_chunk_header: false,
             },
             clock,
             chunk_transactions_time_limit,
@@ -356,11 +361,15 @@ impl ChunkProducer {
 
         let outgoing_receipts_root = self.calculate_receipts_root(epoch_id, &outgoing_receipts)?;
         let gas_used = chunk_extra.gas_used();
+        let gas_limit = chunk_extra.gas_limit();
         #[cfg(feature = "test_features")]
-        let gas_used = if self.adversarial.produce_invalid_chunks {
-            gas_used.checked_add(near_primitives::types::Gas::from_gas(1)).unwrap()
+        let (gas_used, gas_limit) = if self.adversarial.produce_max_gas_chunk_header {
+            // gas_limit too: empty chunks have prev_gas_used == 0, which won't overflow.
+            (Gas::MAX, Gas::MAX)
+        } else if self.adversarial.produce_invalid_chunks {
+            (gas_used.checked_add(Gas::from_gas(1)).unwrap(), gas_limit)
         } else {
-            gas_used
+            (gas_used, gas_limit)
         };
 
         let congestion_info = chunk_extra.congestion_info();
@@ -391,7 +400,7 @@ impl ChunkProducer {
                 next_height,
                 shard_id,
                 gas_used,
-                chunk_extra.gas_limit(),
+                gas_limit,
                 chunk_extra.balance_burnt(),
                 chunk_extra.validator_proposals().collect(),
                 prepared_transactions.transactions,
```

### chain/client/src/client_actor.rs
```diff
@@ -515,6 +515,7 @@ pub enum NetworkAdversarialMessage {
     AdvProduceBlocks(u64, bool),
     AdvProduceChunks(AdvProduceChunksMode),
     AdvInsertInvalidTransactions(bool),
+    AdvProduceMaxGasChunkHeader(bool),
     AdvSwitchToHeight(u64),
     AdvDisableHeaderSync,
     AdvDisableDoomslug,
@@ -605,6 +606,11 @@ impl Handler<NetworkAdversarialMessage, Option<u64>> for ClientActor {
                 self.client.chunk_producer.adversarial.produce_invalid_tx_in_chunks = on;
                 None
             }
+            NetworkAdversarialMessage::AdvProduceMaxGasChunkHeader(on) => {
+                tracing::info!(target: "adversary", on, "max gas chunk header");
+                self.client.chunk_producer.adversarial.produce_max_gas_chunk_header = on;
+                None
+            }
         }
     }
 }
```

### test-loop-tests/src/tests/gas_overflow_optimistic_block.rs
```diff
@@ -0,0 +1,78 @@
+//! Regression test for gas overflow handling in the optimistic-block path.
+//!
+//! Header gas fields are summed across all shards there, before the per-shard
+//! cross-check against `prev_chunk_extra` applies. The sum is therefore fallible:
+//! on overflow, early transaction preparation is skipped rather than panicking.
+
+#![cfg(feature = "test_features")]
+
+use crate::setup::builder::TestLoopBuilder;
+use near_async::time::Duration;
+use near_client::NetworkAdversarialMessage;
+use near_o11y::testonly::init_test_logger;
+use near_primitives::types::BlockHeight;
+use std::mem;
+use std::panic::{AssertUnwindSafe, catch_unwind};
+
+/// Heights the honest validators must still gain after the forgery starts.
+const REQUIRED_PROGRESS: BlockHeight = 5;
+
+/// One chunk producer per shard, so each validator applies only its own shard, as on
+/// mainnet. The forged chunks are never endorsed, so honest validators should keep going.
+#[test]
+// TODO(spice-test): Assess if this test is relevant for spice and if yes fix it.
+#[cfg_attr(feature = "protocol_feature_spice", ignore)]
+fn test_forged_max_gas_chunk_header_does_not_abort_honest_validators() {
+    init_test_logger();
+
+    let num_shards = 4;
+    let mut env = TestLoopBuilder::new()
+        .num_shards(num_shards)
+        .chunk_producer_per_shard()
+        .epoch_length(100)
+        .build();
+
+    // Assert the untracked-shard precondition instead of assuming it.
+    let attacker_idx = num_shards - 1;
+    let attacker_shards = env.node(attacker_idx).tracked_shards();
+    assert!(!attacker_shards.is_empty(), "attacker must produce chunks for some shard");
+    let victim_indices: Vec<usize> = (0..num_shards).filter(|idx| *idx != attacker_idx).collect();
+    for &victim_idx in &victim_indices {
+        let victim_shards = env.node(victim_idx).tracked_shards();
+        assert!(!victim_shards.is_empty(), "victim {victim_idx} must apply some shard");
+        assert!(
+            !victim_shards.iter().any(|shard| attacker_shards.contains(shard)),
+            "victim {victim_idx} tracks {victim_shards:?}, \
+             which overlaps the attacker's {attacker_shards:?}"
+        );
+    }
+
+    let start_height = env.node(0).head().height;
+    env.node_runner(attacker_idx)
+        .send_adversarial_message(NetworkAdversarialMessage::AdvProduceMaxGasChunkHeader(true));
+
+    // Not `#[should_panic]`: `TestLoopEnv::drop` re-enters the loop, so an escaping panic
+    // fires again mid-unwind and aborts the whole test binary.
+    let result = catch_unwind(AssertUnwindSafe(|| {
+        env.test_loop.run_for(Duration::seconds(10));
+    }));
+
+    if let Err(payload) = result {
+        let message = payload
+            .downcast_ref::<String>()
+            .map(String::as_str)
+            .or_else(|| payload.downcast_ref::<&str>().copied())
+            .unwrap_or("<non-string panic payload>")
+            .to_string();
+        mem::forget(env); // dropping it would re-enter the loop, see above
+        panic!("a forged Gas::MAX chunk header took down an honest validator: {message}");
+    }
+
+    for &victim_idx in &victim_indices {
+        let height = env.node(victim_idx).head().height;
+        assert!(
+            height >= start_height + REQUIRED_PROGRESS,
+            "victim {victim_idx} stalled at {height}, started at {start_height}"
+        );
+    }
+}
```

### test-loop-tests/src/tests/mod.rs
```diff
@@ -38,6 +38,7 @@ mod fix_chunk_producer_stake_threshold;
 mod fix_stake_threshold;
 mod garbage_collection;
 mod gas_keys;
+mod gas_overflow_optimistic_block;
 mod genesis_chunk_request;
 mod global_contracts;
 mod global_contracts_distribution;
```
