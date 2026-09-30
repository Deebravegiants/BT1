# [?] [rand] fix the race condition of blocks re-enter

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-09-26
Source: https://github.com/aptos-labs/aptos-core/commit/f5a695e582f9240b81f9289fc4fb5e3a6bda01ae
Type: security-commit

## Details
[rand] fix the race condition of blocks re-enter

## Patch
### consensus/src/rand/rand_gen/rand_manager.rs
```diff
@@ -188,9 +188,7 @@ impl<S: TShare, D: TAugmentedData> RandManager<S, D> {
             ResetSignal::TargetRound(round) => round,
         };
         self.block_queue = BlockQueue::new();
-        self.rand_store
-            .lock()
-            .update_highest_known_round(target_round);
+        self.rand_store.lock().reset(target_round);
         self.stop = matches!(signal, ResetSignal::Stop);
         let _ = tx.send(ResetAck::default());
     }
```

### consensus/src/rand/rand_gen/rand_store.rs
```diff
@@ -250,6 +250,14 @@ impl<S: TShare> RandStore<S> {
         self.highest_known_round = std::cmp::max(self.highest_known_round, round);
     }
 
+    pub fn reset(&mut self, round: u64) {
+        self.update_highest_known_round(round);
+        // remove future rounds items in case they're already decided
+        // otherwise if the block re-enters the queue, it'll be stuck
+        let _ = self.rand_map.split_off(&round);
+        let _ = self.fast_rand_map.as_mut().map(|map| map.split_off(&round));
+    }
+
     pub fn add_rand_metadata(&mut self, rand_metadata: FullRandMetadata) {
         let rand_item = self
             .rand_map
```
