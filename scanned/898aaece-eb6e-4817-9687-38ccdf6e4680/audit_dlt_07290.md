# [?] [garbage_colection] Fix crash in clear_resharding_data while fetching prev_epoch_id (#10195)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2023-11-17
Source: https://github.com/near/nearcore/commit/3eff9716f10895bf80021f853ee56682b57e783f
Type: security-commit

## Details
[garbage_colection] Fix crash in clear_resharding_data while fetching prev_epoch_id (#10195)

We had an issue in the `clear_resharding_data` while fetching the
`prev_epoch_id`. The implementation of `prev_epoch_id` relied on
fetching the block_info of the last block of prev_epoch to get the
epoch_id. This unfortunately failed for the case of GC as the block_info
was already garbage collected.

The new implementation here relies on using the block_header to get the
epoch_id instead of block_info.

This was unfortunately only caught in mocknet and not integration tests
as having a small enough epoch_length lead to the block_info being
cached in the epoch_manager (even though it was GC'd)

Zulip post:
https://near.zulipchat.com/#narrow/stream/295558-pagoda.2Fcore/topic/Master.20binary.20Can't.20clear.20old.20data/near/402240517

Pending: Figure out a way to include test from this PR:
https://github.com/near/nearcore/pull/10193
We would need to enable no_cache feature for the test.

## Patch
### chain/chain/src/store.rs
```diff
@@ -2343,10 +2343,25 @@ impl<'a> ChainStoreUpdate<'a> {
         if !epoch_manager.is_next_block_epoch_start(&block_hash)? {
             return Ok(());
         }
-        let epoch_id = epoch_manager.get_epoch_id(&block_hash)?;
-        let shard_layout = epoch_manager.get_shard_layout(&epoch_id)?;
-        let prev_epoch_id = epoch_manager.get_prev_epoch_id(&block_hash)?;
-        let prev_shard_layout = epoch_manager.get_shard_layout(&prev_epoch_id)?;
+
+        // Since this code is related to GC, we need to be careful about accessing block_infos. Note
+        // that the BlockInfo exists for the current block_hash as it's not been GC'd yet.
+        // However, we need to use the block header to get the epoch_id and shard_layout for
+        // first_block_epoch_header and last_block_prev_epoch_hash as BlockInfo for these blocks is
+        // already GC'd while BlockHeader isn't GC'd.
+        let block_info = epoch_manager.get_block_info(&block_hash)?;
+        let first_block_epoch_hash = block_info.epoch_first_block();
+        if first_block_epoch_hash == &CryptoHash::default() {
+            return Ok(());
+        }
+        let first_block_epoch_header = self.get_block_header(first_block_epoch_hash)?;
+        let last_block_prev_epoch_header =
+            self.get_block_header(first_block_epoch_header.prev_hash())?;
+
+        let epoch_id = first_block_epoch_header.epoch_id();
+        let shard_layout = epoch_manager.get_shard_layout(epoch_id)?;
+        let prev_epoch_id = last_block_prev_epoch_header.epoch_id();
+        let prev_shard_layout = epoch_manager.get_shard_layout(prev_epoch_id)?;
         if shard_layout == prev_shard_layout {
             return Ok(());
         }
```

### chain/chain/src/test_utils/kv_runtime.rs
```diff
@@ -615,13 +615,6 @@ impl EpochManagerAdapter for MockEpochManager {
         }
     }
 
-    fn get_prev_epoch_id(&self, block_hash: &CryptoHash) -> Result<EpochId, EpochError> {
-        let header = self
-            .get_block_header(block_hash)?
-            .ok_or_else(|| EpochError::MissingBlock(*block_hash))?;
-        self.get_prev_epoch_id_from_prev_block(header.prev_hash())
-    }
-
     fn get_prev_epoch_id_from_prev_block(
         &self,
         prev_block_hash: &CryptoHash,
```

### chain/epoch-manager/src/adapter.rs
```diff
@@ -128,8 +128,6 @@ pub trait EpochManagerAdapter: Send + Sync {
     /// Get epoch start from a block belonging to the epoch.
     fn get_epoch_start_height(&self, block_hash: &CryptoHash) -> Result<BlockHeight, EpochError>;
 
-    fn get_prev_epoch_id(&self, block_hash: &CryptoHash) -> Result<EpochId, EpochError>;
-
     /// Get previous epoch id by hash of previous block.
     fn get_prev_epoch_id_from_prev_block(
         &self,
@@ -561,11 +559,6 @@ impl EpochManagerAdapter for EpochManagerHandle {
         epoch_manager.get_epoch_start_height(block_hash)
     }
 
-    fn get_prev_epoch_id(&self, block_hash: &CryptoHash) -> Result<EpochId, EpochError> {
-        let epoch_manager = self.read();
-        epoch_manager.get_prev_epoch_id(block_hash)
-    }
-
     fn get_prev_epoch_id_from_prev_block(
         &self,
         prev_block_hash: &CryptoHash,
```
