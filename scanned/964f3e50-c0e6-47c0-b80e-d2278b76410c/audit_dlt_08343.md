# [?] [Consensus Observer] Fix race condition between commit callback and

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-06-21
Source: https://github.com/aptos-labs/aptos-core/commit/6aca58266648bdafcf26b0514d7efe5050362030
Type: security-commit

## Details
[Consensus Observer] Fix race condition between commit callback and
state sync.

## Patch
### consensus/src/consensus_observer/observer.rs
```diff
@@ -264,8 +264,25 @@ impl ConsensusObserver {
             // Remove the committed blocks from the pending blocks
             remove_pending_blocks(pending_blocks, &ledger_info);
 
-            // Update the root ledger info
-            *root.lock() = ledger_info;
+            // Verify the ledger info is for the same epoch
+            let mut root = root.lock();
+            if ledger_info.commit_info().epoch() != root.commit_info().epoch() {
+                warn!(
+                    LogSchema::new(LogEntry::ConsensusObserver).message(&format!(
+                        "Received commit callback for a different epoch! Ledger info: {:?}, Root: {:?}",
+                        ledger_info.commit_info(),
+                        root.commit_info()
+                    ))
+                );
+                return;
+            }
+
+            // Update the root ledger info. Note: we only want to do this if
+            // the new ledger info round is greater than the current root
+            // round. Otherwise, this can race with the state sync process.
+            if ledger_info.commit_info().round() > root.commit_info().round() {
+                *root = ledger_info;
+            }
         })
     }
 
@@ -425,10 +442,8 @@ impl ConsensusObserver {
         let transaction_payload = BlockTransactionPayload::new(transactions, limit);
         match self.payload_store.lock().entry(block.id()) {
             Entry::Occupied(mut entry) => {
-                // Get the current status of the block payload
-                let mut status = ObserverDataStatus::Available(transaction_payload.clone());
-
                 // Replace the status with the new block payload
+                let mut status = ObserverDataStatus::Available(transaction_payload.clone());
                 mem::swap(entry.get_mut(), &mut status);
 
                 // If the status was originally requested, send the payload to the listener
@@ -607,6 +622,17 @@ impl ConsensusObserver {
             ordered_proof,
         } = ordered_block.clone();
 
+        // Verify that we have at least one ordered block
+        if blocks.is_empty() {
+            warn!(
+                LogSchema::new(LogEntry::ConsensusObserver).message(&format!(
+                    "Received empty ordered block! Ignoring: {:?}",
+                    ordered_proof.commit_info()
+                ))
+            );
+            return;
+        }
+
         // If the block is a child of our last block, we can insert it
         if self.get_last_block().id() == blocks.first().unwrap().parent_id() {
             debug!(
@@ -689,9 +715,9 @@ impl ConsensusObserver {
         if !check_root_epoch_and_round(self.root.clone(), epoch, round) {
             info!(
                 LogSchema::new(LogEntry::ConsensusObserver).message(&format!(
-                "Received outdated sync notification for epoch: {}, round: {}! Current root: {:?}",
+                "Received invalid sync notification for epoch: {}, round: {}! Current root: {:?}",
                 epoch, round, self.root
-            ))
+                ))
             );
             return;
         }
@@ -1093,13 +1119,16 @@ fn remove_payload_blocks(
     }
 }
 
-/// Removes the pending blocks after the given ledger info
+/// Removes the pending blocks before the given ledger info
 fn remove_pending_blocks(
     pending_blocks: Arc<Mutex<BTreeMap<Round, (OrderedBlock, Option<CommitDecision>)>>>,
     ledger_info: &LedgerInfoWithSignatures,
 ) {
-    let mut pending_blocks = pending_blocks.lock();
+    // Determine the round to split off
     let split_off_round = ledger_info.commit_info().round() + 1;
+
+    // Remove the pending blocks before the split off round
+    let mut pending_blocks = pending_blocks.lock();
     *pending_blocks = pending_blocks.split_off(&split_off_round);
 }
 
```
