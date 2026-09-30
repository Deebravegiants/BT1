# [?] Fix "subtract with overflow" when pos force-retire happens early.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2025-11-17
Source: https://github.com/Conflux-Chain/conflux-rust/commit/1a9a7c9219dda23644e8b772e8ddf5bacffd27d5
Type: security-commit

## Details
Fix "subtract with overflow" when pos force-retire happens early.

## Patch
### crates/pos/consensus/executor/src/lib.rs
```diff
@@ -1208,11 +1208,11 @@ impl<V: VMExecutor> BlockExecutor for Executor<V> {
             if !force_retired.is_empty() {
                 // `end_epoch` has been checked above and is excluded below.
                 let end_epoch = ledger_info_with_sigs.ledger_info().epoch();
-                let start_epoch = end_epoch
-                    - POS_STATE_CONFIG.force_retire_check_epoch_count(
+                let start_epoch = end_epoch.saturating_sub(
+                    POS_STATE_CONFIG.force_retire_check_epoch_count(
                         pos_state_to_commit.current_view(),
-                    )
-                    + 1;
+                    ),
+                ) + 1;
                 // Check more past epochs to see if the nodes in `force_retired`
                 // have voted.
                 for end_ledger_info in self
```
