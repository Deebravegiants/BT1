# [?] fixup(sync): make state_tries_updated_tx carry an infallible value, panic-ing when consumer is down is sufficient

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2025-12-15
Source: https://github.com/software-mansion/pathfinder/commit/7d252ffb90ea07e4012266ff1112ada7944fcb69
Type: security-commit

## Details
fixup(sync): make state_tries_updated_tx carry an infallible value, panic-ing when consumer is down is sufficient

## Patch
### crates/pathfinder/src/state/sync.rs
```diff
@@ -61,13 +61,12 @@ pub enum SyncEvent {
     /// responsible for updating the state tries, computing the state
     /// commitment, and finally, the block hash.
     FinalizedConsensusBlock {
-        /// Consensus finalized L2 block, decided upon by conensus.
+        /// L2 block finalized and decided upon by consensus.
         l2_block: Box<ConsensusFinalizedL2Block>,
         /// A oneshot channel to notify when the state tries update is done,
         /// returning the computed block hash and state commitment, which is
         /// necessary for the download block logic to continue its work.
-        state_tries_updated_tx:
-            tokio::sync::oneshot::Sender<anyhow::Result<(BlockHash, StateCommitment)>>,
+        state_tries_updated_tx: tokio::sync::oneshot::Sender<(BlockHash, StateCommitment)>,
     },
     /// An L2 reorg was detected, contains the reorg-tail which
     /// indicates the oldest block which is now invalid
@@ -905,10 +904,11 @@ async fn consumer(
                     )?;
 
                     state_tries_updated_tx
-                        .send(Ok((l2_block.header.hash, l2_block.header.state_commitment)))
-                        // FIXME !!!!
-                        .unwrap();
-                    // .context("Sending state tries updated notification")?;
+                        .send((l2_block.header.hash, l2_block.header.state_commitment))
+                        .expect(
+                            "Receiver was dropped, which means that the consumer task exited and \
+                             all sync related tasks, including this one, will be restarted.",
+                        );
 
                     Some(Notification::L2Block(Arc::new(l2_block)))
                 }
```

### crates/pathfinder/src/state/sync/l2.rs
```diff
@@ -407,11 +407,7 @@ where
                 .context("Event channel closed")?;
             let (block_hash, state_commitment) = rx
                 .await
-                .context("Waiting for state tries to be updated in consumer")?
-                // TODO if the L2 update failed, the consensus sync task will exit and will be
-                // restarted - should we exit the consumer task and restart it too? Or maybe we
-                // should just ignore the error here?
-                .context("L2 update failed")?;
+                .context("Waiting for state tries to be updated in consumer")?;
 
             head = Some((next, block_hash, state_commitment));
             blocks.push(next, block_hash, state_commitment);
```
