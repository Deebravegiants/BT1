# [?] Fix a panic setting `min_phase_change_normal_peer_count` to 0.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-06-22
Source: https://github.com/Conflux-Chain/conflux-rust/commit/76e2cbf384eef16bad5471d53ebe22775efe4f91
Type: security-commit

## Details
Fix a panic setting `min_phase_change_normal_peer_count` to 0.

## Patch
### core/src/sync/synchronization_state.rs
```diff
@@ -238,7 +238,11 @@ impl SynchronizationState {
             }
         };
 
-        if peer_best_epoches.len() < self.min_phase_change_normal_peer_count {
+        // `peer_best_epoches.is_empty()` is only possible if
+        // `self.min_phase_change_normal_peer_count == 0`
+        if peer_best_epoches.len() < self.min_phase_change_normal_peer_count
+            || peer_best_epoches.is_empty()
+        {
             return if fresh_start {
                 debug!("median_epoch_from_normal_peers: fresh start");
                 Some(0)
```
