# [?] [consensus] fix the race condition with the order of operations

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-02-26
Source: https://github.com/aptos-labs/aptos-core/commit/fd8ae4161dacc0ca8d0a92485a30bcba5889d2d2
Type: security-commit

## Details
[consensus] fix the race condition with the order of operations

We send out the epoch change notification before spawning the commit task, so there's race condition that epoch manager
shuts down the buffer manager before the request created and we lose the final commit task.

## Patch
### consensus/src/pipeline/buffer_manager.rs
```diff
@@ -357,17 +357,7 @@ impl BufferManager {
                     self.commit_proof_rb_handle
                         .replace(self.do_reliable_broadcast(commit_decision));
                 }
-                if aggregated_item.commit_proof.ledger_info().ends_epoch() {
-                    self.commit_msg_tx
-                        .send_epoch_change(EpochChangeProof::new(
-                            vec![aggregated_item.commit_proof.clone()],
-                            false,
-                        ))
-                        .await;
-                    // the epoch ends, reset to avoid executing more blocks, execute after
-                    // this persisting request will result in BlockNotFound
-                    self.reset().await;
-                }
+                let commit_proof = aggregated_item.commit_proof.clone();
                 self.persisting_phase_tx
                     .send(self.create_new_request(PersistingRequest {
                         blocks: blocks_to_persist,
@@ -382,6 +372,15 @@ impl BufferManager {
                     }))
                     .await
                     .expect("Failed to send persist request");
+                // this needs to be done after creating the persisting request to avoid it being lost
+                if commit_proof.ledger_info().ends_epoch() {
+                    self.commit_msg_tx
+                        .send_epoch_change(EpochChangeProof::new(vec![commit_proof], false))
+                        .await;
+                    // the epoch ends, reset to avoid executing more blocks, execute after
+                    // this persisting request will result in BlockNotFound
+                    self.reset().await;
+                }
                 info!("Advance head to {:?}", self.buffer.head_cursor());
                 self.previous_commit_time = Instant::now();
                 return;
```
