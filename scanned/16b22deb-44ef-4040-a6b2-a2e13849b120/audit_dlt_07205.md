# [?] fix: Resist CheckpointVerifier memory DoS attacks (#635)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2020-07-15
Source: https://github.com/ZcashFoundation/zebra/commit/851afad01fdde2915e87c2aaee20fb000650900a
Type: security-commit

## Details
fix: Resist CheckpointVerifier memory DoS attacks (#635)

* fix: Resist CheckpointVerifier memory DoS attacks

Allow a maximum of 2 queued blocks at each height, as a tradeoff between
efficient bad block rejection, and memory usage.

Closes #628.

* fix: Make max queued blocks at height equal to fanout

* fix: Just allocate all the capacity upfront

* fix: Use with_capacity(1) and reserve_exact(1)

## Patch
### zebra-consensus/src/checkpoint.rs
```diff
@@ -56,10 +56,24 @@ struct QueuedBlock {
 
 /// A list of unverified blocks at a particular height.
 ///
-/// Typically contains zero or one blocks, but might contain more if a peer
+/// Typically contains a single block, but might contain more if a peer
 /// has an old chain fork. (Or sends us a bad block.)
+///
+/// The CheckpointVerifier avoids creating zero-block lists.
 type QueuedBlockList = Vec<QueuedBlock>;
 
+/// The maximum number of queued blocks at any one height.
+///
+/// This value is a tradeoff between:
+/// - rejecting bad blocks: if we queue more blocks, we need fewer network
+///                         retries, but use a bit more CPU when verifying,
+/// - avoiding a memory DoS: if we queue fewer blocks, we use less memory.
+///
+/// Memory usage is controlled by the sync service, because it controls block
+/// downloads. When the verifier services process blocks, they reduce memory
+/// usage by committing blocks to the disk state. (Or dropping invalid blocks.)
+pub const MAX_QUEUED_BLOCKS_PER_HEIGHT: usize = 4;
+
 /// A checkpointing block verifier.
 ///
 /// Verifies blocks using a supplied list of checkpoints. There must be at
@@ -297,10 +311,26 @@ impl CheckpointVerifier {
             }
         };
 
+        // Since we're using Arc<Block>, each entry is a single pointer to the
+        // Arc. But there are a lot of QueuedBlockLists in the queue, so we keep
+        // allocations as small as possible.
+        let qblocks = self
+            .queued
+            .entry(height)
+            .or_insert_with(|| QueuedBlockList::with_capacity(1));
+
+        // Memory DoS resistance: limit the queued blocks at each height
+        if qblocks.len() >= MAX_QUEUED_BLOCKS_PER_HEIGHT {
+            let _ = tx.send(Err("too many queued blocks at this height".into()));
+            return rx;
+        }
+
         // Add the block to the list of queued blocks at this height
         let hash = block.as_ref().into();
         let new_qblock = QueuedBlock { block, hash, tx };
-        self.queued.entry(height).or_default().push(new_qblock);
+        // This is a no-op for the first block in each QueuedBlockList.
+        qblocks.reserve_exact(1);
+        qblocks.push(new_qblock);
 
         rx
     }
```

### zebrad/src/commands/start/sync.rs
```diff
@@ -10,6 +10,7 @@ use zebra_chain::{
     block::{Block, BlockHeaderHash},
     types::BlockHeight,
 };
+use zebra_consensus::checkpoint;
 use zebra_network::{self as zn, RetryLimit};
 use zebra_state::{self as zs};
 
@@ -38,7 +39,9 @@ where
             verifier,
             retry_peer_set,
             block_requests: FuturesUnordered::new(),
-            fanout: 4,
+            // Limit the fanout to the number of chains that the
+            // CheckpointVerifier can handle
+            fanout: checkpoint::MAX_QUEUED_BLOCKS_PER_HEIGHT,
             prospective_tips: HashSet::new(),
         }
     }
@@ -338,4 +341,4 @@ pub fn block_locator_heights(tip_height: BlockHeight) -> impl Iterator<Item = Bl
 }
 
 type Error = Box<dyn std::error::Error + Send + Sync + 'static>;
-type NumReq = u32;
+type NumReq = usize;
```
