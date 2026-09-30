# [?] fix: improve panic message

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2024-05-27
Source: https://github.com/fedimint/fedimint/commit/43cbb99a8983f77cc60837d7bbb969e9cdd52c21
Type: security-commit

## Details
fix: improve panic message

## Patch
### fedimint-server/src/consensus/debug.rs
```diff
@@ -3,9 +3,9 @@ use std::fmt;
 use crate::ConsensusItem;
 
 /// A newtype for a nice [`fmt::Debug`] of a [`ConsensusItem`]
-pub struct FmtDbgConsensusItem<'ci>(pub &'ci ConsensusItem);
+pub struct DebugConsensusItem<'ci>(pub &'ci ConsensusItem);
 
-impl<'ci> fmt::Debug for FmtDbgConsensusItem<'ci> {
+impl<'ci> fmt::Debug for DebugConsensusItem<'ci> {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
         match self.0 {
             ConsensusItem::Module(mci) => {
```

### fedimint-server/src/consensus/engine.rs
```diff
@@ -41,7 +41,7 @@ use crate::consensus::db::{
     AcceptedItemKey, AcceptedItemPrefix, AcceptedTransactionKey, AlephUnitsPrefix,
     SignedSessionOutcomeKey, SignedSessionOutcomePrefix,
 };
-use crate::consensus::debug_fmt::FmtDbgConsensusItem;
+use crate::consensus::debug::DebugConsensusItem;
 use crate::consensus::transaction::process_transaction_with_dbtx;
 use crate::fedimint_core::encoding::Encodable;
 use crate::metrics::{
@@ -354,14 +354,14 @@ impl ConsensusEngine {
                     assert!(processed.iter().eq(pending_accepted_items.iter()));
 
                     for accepted_item in unprocessed {
-                        let result = self.process_consensus_item(
+                        if self.process_consensus_item(
                             session_index,
                             item_index,
                             accepted_item.item.clone(),
                             accepted_item.peer
-                        ).await;
-
-                        assert!(result.is_ok());
+                        ).await.is_err(){
+                            panic!("Rejected accepted consensus item {:?}", DebugConsensusItem(&accepted_item.item));
+                        }
 
                         item_index += 1;
                     }
@@ -469,7 +469,7 @@ impl ConsensusEngine {
             .with_label_values(&[peer_id_str])
             .start_timer();
 
-        debug!(%peer, item = ?FmtDbgConsensusItem(&item), "Processing consensus item");
+        debug!(%peer, item = ?DebugConsensusItem(&item), "Processing consensus item");
 
         self.last_ci_by_peer
             .write()
```

### fedimint-server/src/consensus/mod.rs
```diff
@@ -3,7 +3,7 @@
 pub mod aleph_bft;
 pub mod api;
 pub mod db;
-pub mod debug_fmt;
+pub mod debug;
 pub mod engine;
 pub mod transaction;
 
```
