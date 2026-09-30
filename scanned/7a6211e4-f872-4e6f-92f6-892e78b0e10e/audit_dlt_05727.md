# [?] fix(mempool): Avoid panicking when a transaction is unexpectedly missing in the mempool (#10049)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2025-11-13
Source: https://github.com/ZcashFoundation/zebra/commit/333f4ffc865096260bea398f0d524a3fa9b5eb86
Type: security-commit

## Details
fix(mempool): Avoid panicking when a transaction is unexpectedly missing in the mempool (#10049)

* Logs a warnings when a dependent transaction id is unexpectedly missing from the mempool's verified set instead of panicking

* - Fixes an issue in `mempool::storage::VerifiedSet::remove_all_that()` where the method could attempt to remove the same transaction twice if it depended on the outputs of another transaction that was just removed.
- Fixes an issue where mined transaction dependencies were not being removed from the mempool's transaction dependencies.

* fixes clippy lint

* Updates `TransactionDependencies::remove_all()` to remove tracked dependent transaction ids for a transaction when removing those dependent transaction.

Updates `clear_mined_dependencies()` to remove keys in the `dependencies` map with empty values.

## Patch
### zebra-node-services/src/mempool/transaction_dependencies.rs
```diff
@@ -49,7 +49,7 @@ impl TransactionDependencies {
                 .insert(dependent);
         }
 
-        // Only add an entries to `dependencies` for transactions that spend unmined outputs so it
+        // Only add entries to `dependencies` for transactions that spend unmined outputs so it
         // can be used to handle transactions with dependencies differently during block production.
         if !spent_mempool_outpoints.is_empty() {
             self.dependencies.insert(
@@ -73,7 +73,10 @@ impl TransactionDependencies {
                 };
 
                 // TODO: Move this struct to zebra-chain and log a warning here if the dependency was not found.
-                let _ = dependencies.remove(&dependent_id);
+                dependencies.remove(mined_tx_id);
+                if dependencies.is_empty() {
+                    self.dependencies.remove(&dependent_id);
+                }
             }
         }
     }
@@ -91,9 +94,20 @@ impl TransactionDependencies {
         while !current_level_dependents.is_empty() {
             current_level_dependents = current_level_dependents
                 .iter()
-                .flat_map(|dep| {
-                    self.dependencies.remove(dep);
-                    self.dependents.remove(dep).unwrap_or_default()
+                .flat_map(|dependent| {
+                    for dependency in self.dependencies.remove(dependent).unwrap_or_default() {
+                        let Some(dependents_of_dependency) = self.dependents.get_mut(&dependency)
+                        else {
+                            continue;
+                        };
+
+                        dependents_of_dependency.remove(dependent);
+                        if dependents_of_dependency.is_empty() {
+                            self.dependents.remove(&dependency);
+                        }
+                    }
+
+                    self.dependents.remove(dependent).unwrap_or_default()
                 })
                 .collect();
 
```

### zebrad/src/components/mempool/storage/verified_set.rs
```diff
@@ -256,6 +256,11 @@ impl VerifiedSet {
         let mut removed_transactions = HashSet::new();
 
         for key_to_remove in keys_to_remove {
+            if !self.transactions.contains_key(&key_to_remove) {
+                // Skip any keys that may have already been removed as their dependencies were removed.
+                continue;
+            }
+
             removed_transactions.extend(
                 self.remove(&key_to_remove)
                     .into_iter()
@@ -281,17 +286,17 @@ impl VerifiedSet {
             .remove_all(key_to_remove)
             .iter()
             .chain(std::iter::once(key_to_remove))
-            .map(|key_to_remove| {
-                let removed_tx = self
-                    .transactions
-                    .remove(key_to_remove)
-                    .expect("invalid transaction key");
+            .filter_map(|key_to_remove| {
+                let Some(removed_tx) = self.transactions.remove(key_to_remove) else {
+                    tracing::warn!(?key_to_remove, "invalid transaction key");
+                    return None;
+                };
 
                 self.transactions_serialized_size -= removed_tx.transaction.size;
                 self.total_cost -= removed_tx.cost();
                 self.remove_outputs(&removed_tx.transaction);
 
-                removed_tx
+                Some(removed_tx)
             })
             .collect();
 
```
