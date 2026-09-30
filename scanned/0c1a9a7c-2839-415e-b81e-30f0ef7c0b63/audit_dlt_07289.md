# [?] fix: don't panic when a Client receives ChunkStateWitness with invalid shard_id (#10621)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-02-21
Source: https://github.com/near/nearcore/commit/fc79a6727744f251f17ecb4116ca9398821ae74a
Type: security-commit

## Details
fix: don't panic when a Client receives ChunkStateWitness with invalid shard_id (#10621)

When Client start processing a new `ChunkStateWitness` which it
received, it immediately fetches the previous block and the previous
chunk using `prev_block_hash` and `shard_id` provided by the
`ChunkStateWitness`.
It turns out that the current implementation of
`Chain::get_prev_chunk_header` will panic if it's given an invalid
`shard_id`, which means that a malicious peer could send a
`ChunkStateWitness` with a bad `shard_id` and it would crash the node
that received it.


https://github.com/near/nearcore/blob/c5c84adbadf54957083a33ec243cb334b411daee/chain/client/src/stateless_validation/chunk_validator.rs#L596-L607

`Chain::get_prev_chunk_header` is very deceptive, it returns a `Result`,
but still does an `unwrap()` inside. Let's fix the problem by removing
the `unwrap()`. From now on `Chain::get_prev_chunk_header` will return a
error when it encounters an invalid `shard_id`.

A test is added to ensure that this bug doesn't happen again.

## Patch
### chain/chain/src/chain.rs
```diff
@@ -4182,8 +4182,12 @@ impl Chain {
         prev_block: &Block,
         shard_id: ShardId,
     ) -> Result<ShardChunkHeader, Error> {
-        let prev_shard_id = epoch_manager.get_prev_shard_ids(prev_block.hash(), vec![shard_id])?[0];
-        Ok(prev_block.chunks().get(prev_shard_id as usize).unwrap().clone())
+        let prev_shard_id = epoch_manager.get_prev_shard_id(prev_block.hash(), shard_id)?;
+        Ok(prev_block
+            .chunks()
+            .get(prev_shard_id as usize)
+            .ok_or(Error::InvalidShardId(shard_id))?
+            .clone())
     }
 
     pub fn group_receipts_by_shard(
```

### chain/chain/src/test_utils/kv_runtime.rs
```diff
@@ -589,6 +589,14 @@ impl EpochManagerAdapter for MockEpochManager {
         Ok(shard_ids)
     }
 
+    fn get_prev_shard_id(
+        &self,
+        _prev_hash: &CryptoHash,
+        shard_id: ShardId,
+    ) -> Result<ShardId, Error> {
+        Ok(shard_id)
+    }
+
     fn get_shard_layout_from_prev_block(
         &self,
         _parent_hash: &CryptoHash,
```

### chain/epoch-manager/src/adapter.rs
```diff
@@ -113,12 +113,26 @@ pub trait EpochManagerAdapter: Send + Sync {
     ///
     /// Most of the times parent of the shard is the shard itself, unless a
     /// resharding happened and some shards were split.
+    /// If there was no resharding, it just returns `shard_ids` as is, without any validation.
+    /// The resulting Vec will always be of the same length as the `shard_ids` argument.
     fn get_prev_shard_ids(
         &self,
         prev_hash: &CryptoHash,
         shard_ids: Vec<ShardId>,
     ) -> Result<Vec<ShardId>, Error>;
 
+    /// For a `ShardId` in the current block, returns its parent `ShardId`
+    /// from previous block.
+    ///
+    /// Most of the times parent of the shard is the shard itself, unless a
+    /// resharding happened and some shards were split.
+    /// If there was no resharding, it just returns the `shard_id` as is, without any validation.
+    fn get_prev_shard_id(
+        &self,
+        prev_hash: &CryptoHash,
+        shard_id: ShardId,
+    ) -> Result<ShardId, Error>;
+
     /// Get shard layout given hash of previous block.
     fn get_shard_layout_from_prev_block(
         &self,
@@ -574,6 +588,28 @@ impl EpochManagerAdapter for EpochManagerHandle {
         Ok(shard_ids)
     }
 
+    fn get_prev_shard_id(
+        &self,
+        prev_hash: &CryptoHash,
+        shard_id: ShardId,
+    ) -> Result<ShardId, Error> {
+        if self.is_next_block_epoch_start(prev_hash)? {
+            let shard_layout = self.get_shard_layout_from_prev_block(prev_hash)?;
+            let prev_shard_layout = self.get_shard_layout(&self.get_epoch_id(prev_hash)?)?;
+            if prev_shard_layout != shard_layout {
+                let parent_shard_id = shard_layout.get_parent_shard_id(shard_id)?;
+                assert!(prev_shard_layout.shard_ids().any(|i| i == parent_shard_id),
+                                    "invalid shard layout.  parent_shard_id: {}\nshard_layout: {:?}\nprev_shard_layout: {:?}",
+                                    parent_shard_id,
+                                    shard_layout,
+                                    parent_shard_id
+                            );
+                return Ok(parent_shard_id);
+            }
+        }
+        Ok(shard_id)
+    }
+
     fn get_shard_layout_from_prev_block(
         &self,
         parent_hash: &CryptoHash,
```

### integration-tests/src/tests/client/features/stateless_validation.rs
```diff
@@ -1,5 +1,10 @@
 use near_epoch_manager::{EpochManager, EpochManagerAdapter};
+use near_primitives::network::PeerId;
+use near_primitives::sharding::{ShardChunkHeader, ShardChunkHeaderV3};
+use near_primitives::stateless_validation::ChunkStateWitness;
+use near_primitives::validator_signer::EmptyValidatorSigner;
 use near_store::test_utils::create_test_store;
+use nearcore::config::GenesisExt;
 use rand::rngs::StdRng;
 use rand::{Rng, SeedableRng};
 use std::collections::HashSet;
@@ -312,3 +317,59 @@ fn test_protocol_upgrade_81() {
         }
     }
 }
+
+/// Test that Client rejects ChunkStateWitnesses with invalid shard_id
+#[test]
+fn test_chunk_state_witness_bad_shard_id() {
+    init_integration_logger();
+
+    if !checked_feature!("stable", StatelessValidationV0, PROTOCOL_VERSION) {
+        println!("Test not applicable without StatelessValidation enabled");
+        return;
+    }
+
+    let accounts = vec!["test0".parse().unwrap()];
+    let genesis = Genesis::test(accounts.clone(), 1);
+    let mut env = TestEnv::builder(&genesis.config)
+        .validators(accounts)
+        .nightshade_runtimes(&genesis)
+        .build();
+
+    // Run the client for a few blocks
+    let upper_height = 6;
+    for height in 1..upper_height {
+        tracing::info!(target: "test", "Producing block at height: {height}");
+        let block = env.clients[0].produce_block(height).unwrap().unwrap();
+        env.process_block(0, block, Provenance::PRODUCED);
+    }
+
+    // Create a dummy ChunkStateWitness with an invalid shard_id
+    let previous_block = env.clients[0].chain.head().unwrap().prev_block_hash;
+    let invalid_shard_id = 1000000000;
+
+    let shard_header = ShardChunkHeader::V3(ShardChunkHeaderV3::new(
+        previous_block,
+        Default::default(),
+        Default::default(),
+        Default::default(),
+        Default::default(),
+        upper_height,
+        invalid_shard_id,
+        Default::default(),
+        Default::default(),
+        Default::default(),
+        Default::default(),
+        Default::default(),
+        Default::default(),
+        &EmptyValidatorSigner::default(),
+    ));
+    let witness = ChunkStateWitness::empty(shard_header);
+
+    // Client should reject this ChunkStateWitness and the error message should mention "shard"
+    tracing::info!(target: "test", "Processing invalid ChunkStateWitness");
+    let res = env.clients[0].process_chunk_state_witness(witness, PeerId::random(), None);
+    let error = res.unwrap_err();
+    let error_message = format!("{}", error).to_lowercase();
+    tracing::info!(target: "test", "error message: {}", error_message);
+    assert!(error_message.contains("shard"));
+}
```
