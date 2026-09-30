# [?] [consensus] Fix rand manager deadlock in multi-block batches (#19359)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-07
Source: https://github.com/aptos-labs/aptos-core/commit/fefcfade3edf26f0396d63963f7ea04364f3666f
Type: security-commit

## Details
[consensus] Fix rand manager deadlock in multi-block batches (#19359)

PR #18699 introduced a circular dependency for multi-block ordering
batches: later blocks' has_rand_txns_fut waits for earlier blocks'
execute_fut, which waits for rand_rx, which is only sent after the
entire batch is dequeued from the rand manager — but dequeue requires
all blocks' randomness to be decided first.

Fix: eagerly send rand_tx in PipelinedBlock::set_randomness (matching
the pattern of set_decryption_key), so the pipeline is unblocked as
soon as randomness is decided per-block. The execution_schedule_phase
already handles this idempotently via .take().

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### consensus/consensus-types/src/pipelined_block.rs
```diff
@@ -368,8 +368,19 @@ impl PipelinedBlock {
         }
     }
 
+    /// Stores the randomness on the block and eagerly sends it via the pipeline channel
+    /// to unblock the execution phase as early as possible. Without this, later blocks
+    /// in the same ordering batch deadlock: their has_rand_txns_fut waits for earlier
+    /// blocks' execute_fut, which waits for rand_rx. The execution_schedule_phase also
+    /// sends via this channel as a fallback (using take(), so only one send actually occurs).
     pub fn set_randomness(&self, randomness: Randomness) {
-        assert!(self.randomness.set(randomness.clone()).is_ok());
+        assert!(self.randomness.set(randomness).is_ok());
+        if let Some(tx) = self.pipeline_tx().lock().as_mut() {
+            let _ = tx
+                .rand_tx
+                .take()
+                .map(|tx| tx.send(self.randomness().cloned()));
+        }
     }
 
     /// Stores the decryption key on the block and eagerly sends it via the pipeline channel
```

### consensus/src/rand/rand_gen/block_queue.rs
```diff
@@ -161,8 +161,10 @@ mod tests {
         block_queue::{BlockQueue, QueueItem},
         test_utils::create_ordered_blocks,
     };
+    use aptos_consensus_types::pipelined_block::PipelineInputTx;
     use aptos_types::randomness::Randomness;
     use std::collections::HashSet;
+    use tokio::sync::oneshot;
 
     #[test]
     fn test_queue_item() {
@@ -231,4 +233,52 @@ mod tests {
 
         assert_eq!(queue.queue.len(), 1);
     }
+
+    /// Test that set_randomness immediately sends rand_tx to unblock the pipeline.
+    /// Without this, multi-block batches deadlock: later blocks' has_rand_txns_fut
+    /// waits for earlier blocks' execute_fut, which waits for rand_rx, which is
+    /// normally only sent after the entire batch is dequeued.
+    #[test]
+    fn test_set_randomness_sends_rand_tx_immediately() {
+        let ordered_blocks = create_ordered_blocks(vec![1, 2]);
+        let mut rand_rxs = vec![];
+
+        // Wire up pipeline_tx with rand_tx/rand_rx for each block
+        for block in &ordered_blocks.ordered_blocks {
+            let (rand_tx, rand_rx) = oneshot::channel();
+            block.set_pipeline_tx(PipelineInputTx {
+                qc_tx: None,
+                rand_tx: Some(rand_tx),
+                order_vote_tx: None,
+                ordered_blocks_and_proof_fut: None,
+                commit_proof_tx: None,
+                secret_shared_key_tx: None,
+            });
+            rand_rxs.push(rand_rx);
+        }
+
+        let mut item = QueueItem::new(ordered_blocks, None);
+
+        // Set randomness on block 1 — rand_rx should fire immediately
+        assert!(item.set_randomness(1, Randomness::default()));
+        let result = rand_rxs[0].try_recv();
+        assert!(
+            result.is_ok(),
+            "rand_tx for block 1 should be sent immediately on set_randomness"
+        );
+
+        // Block 2 rand_rx should NOT have fired yet
+        assert!(
+            rand_rxs[1].try_recv().is_err(),
+            "rand_tx for block 2 should not be sent yet"
+        );
+
+        // Set randomness on block 2
+        assert!(item.set_randomness(2, Randomness::default()));
+        let result = rand_rxs[1].try_recv();
+        assert!(
+            result.is_ok(),
+            "rand_tx for block 2 should be sent immediately on set_randomness"
+        );
+    }
 }
```
