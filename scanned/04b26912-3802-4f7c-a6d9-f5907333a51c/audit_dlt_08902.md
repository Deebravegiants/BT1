# [?] fix: race condition

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-01-05
Source: https://github.com/software-mansion/pathfinder/commit/53f1bb1c3c41ff144a97c457390290ab9ba0ab91
Type: security-commit

## Details
fix: race condition

## Patch
### crates/pathfinder/src/state/sync.rs
```diff
@@ -794,13 +794,13 @@ async fn consumer(
 
             let pruning_event = PruningEvent::from_sync_event(&event);
 
-            let notification = match event {
+            let (notification, sync_to_consensus_msg) = match event {
                 L1Update(update) => {
                     tracing::trace!("Updating L1 sync to block {}", update.block_number);
                     l1_update(&tx, &update)?;
                     tracing::info!("L1 sync updated to block {}", update.block_number);
 
-                    None
+                    (None, None)
                 }
                 DownloadedBlock(
                     (block, (tx_comm, ev_comm, rc_comm)),
@@ -897,7 +897,7 @@ async fn consumer(
                         }
                     }
 
-                    Some(Notification::L2Block(Arc::new(l2_block)))
+                    (Some(Notification::L2Block(Arc::new(l2_block))), None)
                 }
                 FinalizedConsensusBlock {
                     l2_block,
@@ -926,7 +926,14 @@ async fn consumer(
                              all sync related tasks, including this one, will be restarted.",
                         );
 
-                    Some(Notification::L2Block(Arc::new(l2_block)))
+                    // FIXME there should be another notification for blocks coming from consensus
+                    // that were finalized
+                    (
+                        Some(Notification::L2Block(Arc::new(l2_block))),
+                        Some(SyncMessageToConsensus::ConfirmFinalizedBlockCommitted {
+                            number: l2_block.header.number,
+                        }),
+                    )
                 }
                 Reorg(reorg_tail) => {
                     tracing::trace!("Reorg L2 state to block {}", reorg_tail);
@@ -947,7 +954,7 @@ async fn consumer(
                         None => tracing::info!("L2 reorg occurred, new L2 head is genesis"),
                     }
 
-                    Some(Notification::L2Reorg(reorg))
+                    (Some(Notification::L2Reorg(reorg)), None)
                 }
                 CairoClass { definition, hash } => {
                     tracing::trace!("Inserting new Cairo class with hash: {hash}");
@@ -956,7 +963,7 @@ async fn consumer(
 
                     tracing::debug!(%hash, "Inserted new Cairo class");
 
-                    None
+                    (None, None)
                 }
                 SierraClass {
                     sierra_definition,
@@ -976,7 +983,7 @@ async fn consumer(
 
                     tracing::debug!(sierra=%sierra_hash, casm=%casm_hash, "Inserted new Sierra class");
 
-                    None
+                    (None, None)
                 }
                 Pending((pending_block, pending_state_update)) => {
                     tracing::trace!("Updating pending data");
@@ -995,7 +1002,7 @@ async fn consumer(
                         tracing::debug!("Updated pending data");
                     }
 
-                    None
+                    (None, None)
                 }
                 PreConfirmed {
                     number,
@@ -1032,7 +1039,7 @@ async fn consumer(
                         }
                     }
 
-                    None
+                    (None, None)
                 }
             };
 
@@ -1058,14 +1065,20 @@ async fn consumer(
             if let Some(notification) = notification {
                 send_notification(notification, &mut notifications);
             }
-
             // TODO return the value of the committed l2 block
             commit_result.map(|_| maybe_committed_l2_block_number)
         })?;
 
         if let Some(committed_l2_block_number) = maybe_committed_l2_block_number {
             // Notify consensus that a new L2 block has been committed.
             if let Some(sync_to_consensus_tx) = sync_to_consensus_tx.clone() {
+                //
+                // FIXME
+                // BUG
+                // this notification should only be sent in a block that was taken from
+                // consensus was committed and not when a block that was downloaded from an FGW
+                // was committed BUG
+                //
                 sync_to_consensus_tx
                     .send(SyncMessageToConsensus::ConfirmFinalizedBlockCommitted {
                         number: committed_l2_block_number,
```

### crates/pathfinder/src/state/sync/l2.rs
```diff
@@ -425,6 +425,14 @@ where
             .await
             .context("Receiving committed block from consensus")?;
 
+        // IMPORTANT
+        // A race condition can occur in fast local networks:
+        // - Alice commits @H
+        // - FGw uses Alice's DB directly, so it also serves H immediately
+        // - Bob hasn't committed @H yet, even though he voted on it, so he asks for it
+        //   from FGw
+        // - Bob downloads @H from FGw, even though he will shortly have it ready for
+        //   committing localy from his own consensus engine
         if let Some(l2_block) = reply {
             let (state_tries_updated_tx, rx) = tokio::sync::oneshot::channel();
 
@@ -476,17 +484,37 @@ where
                     break (block, commitments, state_update, state_diff_commitment);
                 }
                 DownloadBlock::Wait => {
-                    // Now try from consensus
-                    continue 'outer;
-
-                    // Wait for the latest block to change.
-                    if latest
-                        .wait_for(|x| x.is_some_and(|(_, hash)| hash != head.unwrap_or_default().1))
-                        .await
-                        .is_err()
-                    {
-                        tracing::debug!("Latest tracking channel closed, exiting");
-                        return Ok(());
+                    let fgw_fut = latest.wait_for(|x| {
+                        x.is_some_and(|(_, hash)| hash != head.unwrap_or_default().1)
+                    });
+                    let consensus_fut = consensus_info_watch.changed();
+
+                    tokio::select! {
+                        biased;
+
+                        res = consensus_fut => {
+                            match res {
+                                Ok(_) => {
+                                    tracing::trace!("YYYY 013 Consensus info watch changed, trying to get the block from consensus {next}");
+                                    continue 'outer;
+                                }
+                                Err(_) => {
+                                    tracing::debug!("Consensus info watch closed, exiting");
+                                    return Ok(());
+                                }
+                            }
+                        }
+                        res = fgw_fut => {
+                            match res {
+                                Ok(_) => {
+                                    tracing::trace!("YYYY 013 Feeder gateway latest watch changed, retrying download for block {next}");
+                                }
+                                Err(_) => {
+                                    tracing::debug!("Feeder gateway latest watch closed, exiting");
+                                    return Ok(());
+                                }
+                            }
+                        }
                     }
                 }
                 DownloadBlock::Retry => {
```
