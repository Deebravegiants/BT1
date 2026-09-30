# [?] Fix panic expectations

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-05-02
Source: https://github.com/MystenLabs/sui/commit/9bff2e17ce34110ddeb52758de22a47c146820bb
Type: security-commit

## Details
Fix panic expectations

## Patch
### crates/sui-analytics-indexer/src/package_store/cache_coordinator.rs
```diff
@@ -28,11 +28,11 @@ impl CacheReadyCoordinator {
 
     pub fn mark_ready(&self, checkpoint: u64) {
         let prev = self.latest.swap(checkpoint, Ordering::SeqCst);
-        if checkpoint > prev {
+        if prev == 0 || checkpoint == prev + 1 {
             let _ = self.tx.send_replace(checkpoint);
         } else {
             // Should never happen since concurrency is set to 1.
-            panic!("Package cache coordinator saw checkpoints out of order.");
+            panic!("Package cache coordinator saw checkpoints out of order. Previous: {prev}. Current: {checkpoint}");
         }
     }
 
```
