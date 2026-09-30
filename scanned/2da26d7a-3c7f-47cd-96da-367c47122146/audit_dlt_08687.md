# [?] Fixes underflow bug in validator inactivity jailing

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2023-11-14
Source: https://github.com/namada-net/namada/commit/87d13c80652e0f3d60f24d7c3c431bdd05aa19f1
Type: security-commit

## Details
Fixes underflow bug in validator inactivity jailing

## Patch
### proof_of_stake/src/lib.rs
```diff
@@ -5720,28 +5720,31 @@ where
         .map(|vote| (&vote.validator_address))
         .collect::<HashSet<&Address>>();
 
-    let prune_height = block_height - LIVENESS_BLOCKS_NUM;
+    let prune_height = block_height.0.checked_sub(LIVENESS_BLOCKS_NUM);
 
     for validator_address in consensus_validator_set.into_iter() {
         // Prune old vote (only need to look for the block height that was just
         // pushed out of the sliding window)
-        let pruned_missing_vote = liveness_record
-            .at(&validator_address)
-            .remove(storage, &prune_height)?;
+        if let Some(prune_height) = prune_height {
+            let pruned_missing_vote = liveness_record
+                .at(&validator_address)
+                .remove(storage, &prune_height.into())?;
 
-        if pruned_missing_vote {
-            // Update liveness data
-            liveness_data.update(
-                storage,
-                validator_address.clone(),
-                |missed_votes| {
-                    let missed_votes = missed_votes.expect(&format!(
-                        "Expected liveness data for validator {} was not found",
-                        validator_address
-                    ));
-                    missed_votes - 1
-                },
-            )?;
+            if pruned_missing_vote {
+                // Update liveness data
+                liveness_data.update(
+                    storage,
+                    validator_address.clone(),
+                    |missed_votes| {
+                        let missed_votes = missed_votes.expect(&format!(
+                            "Expected liveness data for validator {} was not \
+                             found",
+                            validator_address
+                        ));
+                        missed_votes - 1
+                    },
+                )?;
+            }
         }
 
         // Evaluate new vote
```
