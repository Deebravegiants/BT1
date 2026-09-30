# [?] fix - fix race condition in chunk validator assignment logic (#14864)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-01-09
Source: https://github.com/near/nearcore/commit/7f8bbbbf3cd570fa8fb95b50420f08210714016f
Type: security-commit

## Details
fix - fix race condition in chunk validator assignment logic (#14864)

I don't think this is the issue but eliminating that possibility can
still help.

## Patch
### chain/epoch-manager/src/lib.rs
```diff
@@ -902,6 +902,8 @@ impl EpochManager {
         if let Some(chunk_validators) = self.chunk_validators_cache.get(&cache_key) {
             return Ok(chunk_validators);
         }
+        let requested_cache_key = cache_key;
+        let mut result = None;
 
         let epoch_info = self.get_epoch_info(epoch_id)?;
         let shard_layout = self.get_shard_layout(epoch_id)?;
@@ -914,17 +916,25 @@ impl EpochManager {
                 })
                 .collect();
             let shard_id = shard_layout.get_shard_id(shard_index)?;
+            let value = Arc::new(ChunkValidatorAssignments::new(chunk_validators));
             let cache_key = (*epoch_id, shard_id, height);
-            self.chunk_validators_cache
-                .put(cache_key, Arc::new(ChunkValidatorAssignments::new(chunk_validators)));
+            // Preserve the result on the off-chance that the cache is fully
+            // replaced before we finish populating it and try to read the
+            // result from the cache.
+            if cache_key == requested_cache_key {
+                result = Some(Arc::clone(&value));
+            }
+            self.chunk_validators_cache.put(cache_key, value);
         }
 
-        self.chunk_validators_cache.get(&cache_key).ok_or_else(|| {
-            EpochError::ChunkValidatorSelectionError(format!(
-                "Invalid shard ID {} for height {}, epoch {:?} for chunk validation",
-                shard_id, height, epoch_id,
-            ))
-        })
+        if let Some(result) = result {
+            return Ok(result);
+        }
+
+        Err(EpochError::ChunkValidatorSelectionError(format!(
+            "Invalid shard ID {} for height {}, epoch {:?} for chunk validation",
+            shard_id, height, epoch_id,
+        )))
     }
 
     pub fn get_all_block_approvers_ordered(
```
