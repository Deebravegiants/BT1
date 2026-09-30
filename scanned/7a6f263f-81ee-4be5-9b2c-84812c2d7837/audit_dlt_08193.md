# [?] blockstore_processor: fix BlockFooter race condition (#12780)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-05-28
Source: https://github.com/anza-xyz/agave/commit/52e9e4b4ae5f12d3aad74f797131f8d21406b527
Type: security-commit

## Details
blockstore_processor: fix BlockFooter race condition (#12780)

* blockstore_processor: fix BlockFooter race condition

* pr feedback: fix leader side

## Patch
### core/src/block_creation_loop.rs
```diff
@@ -733,7 +733,7 @@ fn record_and_complete_block(
         "optimistic_parent should be None after receiving ParentReady"
     );
 
-    // Alpentick and clear bank
+    // Alpentick, produce the footer, and clear bank
     let mut w_poh_recorder = ctx.poh_recorder.write().unwrap();
     let bank = w_poh_recorder
         .bank()
@@ -762,6 +762,10 @@ fn record_and_complete_block(
         let footer = produce_block_footer(&bank, skip, notar, guard.as_ref());
         let final_cert_input = guard.as_ref().map(|c| c.vote_rewards_input());
 
+        // BankingStage may still be executing batches that were already recorded.
+        // Footer processing mutates vote accounts directly, so wait for execution to complete first.
+        bank.wait_for_inflight_commits();
+
         BlockComponentProcessor::update_bank_with_footer_fields(
             &bank,
             i64::try_from(footer.block_producer_time_nanos)
```

### entry/src/block_component.rs
```diff
@@ -446,6 +446,20 @@ impl VersionedBlockMarker {
         let g = BlockMarkerV1::GenesisCertificate(LengthPrefixed::new(g));
         VersionedBlockMarker::V1(g)
     }
+
+    pub fn is_update_parent(&self) -> bool {
+        match self {
+            VersionedBlockMarker::V1(BlockMarkerV1::UpdateParent(_)) => true,
+            VersionedBlockMarker::V1(_) => false,
+        }
+    }
+
+    pub fn is_footer(&self) -> bool {
+        match self {
+            VersionedBlockMarker::V1(BlockMarkerV1::BlockFooter(_)) => true,
+            VersionedBlockMarker::V1(_) => false,
+        }
+    }
 }
 
 #[derive(Debug, Clone, PartialEq, Eq)]
```

### ledger/src/blockstore_processor.rs
```diff
@@ -22,7 +22,7 @@ use {
     solana_clock::Slot,
     solana_cost_model::{cost_model::CostModel, transaction_cost::TransactionCost},
     solana_entry::{
-        block_component::{BlockComponent, VersionedBlockMarker},
+        block_component::BlockComponent,
         entry::{self, Entry, EntrySlice, EntryType, create_ticks},
     },
     solana_genesis_config::GenesisConfig,
@@ -1861,13 +1861,17 @@ fn confirm_slot_with_components(
                 )?;
             }
             BlockComponent::BlockMarker(marker) => {
+                if marker.is_footer() {
+                    // The footer path mutates vote accounts directly to pay rewards.
+                    // All prior transactions must finish first so vote account view is deterministic.
+                    if let Some((result, execute_time)) = bank.wait_for_completed_scheduler() {
+                        timing.batch_execute.totals.accumulate(&execute_time);
+                        result?;
+                    }
+                }
                 if let Some(parent_bank) = bank.parent() {
-                    let allow_initial_update_parent = replay_starts_at_update_parent
-                        && matches!(
-                            &marker,
-                            VersionedBlockMarker::V1(marker)
-                                if marker.as_update_parent().is_some()
-                        );
+                    let allow_initial_update_parent =
+                        replay_starts_at_update_parent && marker.is_update_parent();
                     processor
                         .on_marker(
                             bank.clone_without_scheduler(),
```
