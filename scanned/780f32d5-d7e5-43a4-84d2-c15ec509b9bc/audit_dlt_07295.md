# [?] fix: don't panic on SIGTERM during flat storage creation (#9070)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2023-05-19
Source: https://github.com/near/nearcore/commit/f85ef73f0d2bd65902a026f13bbafd6954e8e9b4
Type: security-commit

## Details
fix: don't panic on SIGTERM during flat storage creation (#9070)

Fixes panicking of threads fetching state on flat storage creation.

If binary is stopped by SIGTERM, channel for receiving messages with state part stats can be disconnected. We shouldn't panic in such case, it's enough to log an error. Still, the node will stall for ~5 minutes because existing rayon threads need to finish heavy IO work. 

Original thread https://near.zulipchat.com/#narrow/stream/308695-pagoda.2Fprivate/topic/Flat.20storage.20crash.20on.20SIGTERM.201.2E34-RC1/near/358803319

## Patch
### chain/chain/src/flat_storage_creator.rs
```diff
@@ -130,7 +130,16 @@ impl FlatStorageShardCreator {
             proccessed parts: {processed_parts}"
         );
 
-        result_sender.send(num_items).unwrap();
+        if let Err(e) = result_sender.send(num_items) {
+            // Log error with `eprintln` because `tracing` stops working after
+            // SIGTERM.
+            eprintln!(
+                "During flat storage creation, state part sender channel \
+                was disconnected: {e}. Results of fetching state part \
+                {part_id:?} for shard {shard_uid} will not be recorded \
+                and flat storage creation will stall. Please restart the node."
+            );
+        }
     }
 
     /// Checks current flat storage creation status, execute work related to it and possibly switch to next status.
```
