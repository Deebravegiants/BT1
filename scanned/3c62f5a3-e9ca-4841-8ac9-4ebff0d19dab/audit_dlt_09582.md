# [?] Fix a possible underflow panic in txpool.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2021-11-17
Source: https://github.com/Conflux-Chain/conflux-rust/commit/1eb42c49514e7d26e9d47b68c836c4b4ff791814
Type: security-commit

## Details
Fix a possible underflow panic in txpool.

## Patch
### core/src/transaction_pool/transaction_pool_inner.rs
```diff
@@ -432,13 +432,6 @@ impl TransactionPoolInner {
                 warn!("an unexecuted tx is garbage-collected.");
             }
 
-            if !self
-                .deferred_pool
-                .check_tx_packed(addr.clone(), to_remove_tx.nonce)
-            {
-                self.unpacked_transaction_count -= 1;
-            }
-
             // maintain ready account pool
             if let Some(ready_tx) = self.ready_account_pool.get(&addr) {
                 if ready_tx.hash() == to_remove_tx.hash() {
@@ -453,6 +446,19 @@ impl TransactionPoolInner {
                 }
             }
 
+            if !self
+                .deferred_pool
+                .check_tx_packed(addr.clone(), to_remove_tx.nonce)
+            {
+                self.unpacked_transaction_count = self
+                    .unpacked_transaction_count
+                    .checked_sub(1)
+                    .unwrap_or_else(|| {
+                        error!("unpacked_transaction_count under-flows.");
+                        0
+                    });
+            }
+
             let removed_tx = self
                 .deferred_pool
                 .remove_lowest_nonce(&addr)
@@ -564,7 +570,13 @@ impl TransactionPoolInner {
             InsertResult::Failed(_) => {}
             InsertResult::Updated(replaced_tx) => {
                 if !replaced_tx.is_already_packed() {
-                    self.unpacked_transaction_count -= 1;
+                    self.unpacked_transaction_count = self
+                        .unpacked_transaction_count
+                        .checked_sub(1)
+                        .unwrap_or_else(|| {
+                            error!("unpacked_transaction_count under-flows.");
+                            0
+                        });
                 }
                 self.txs.remove(&replaced_tx.hash());
                 self.txs.insert(transaction.hash(), transaction.clone());
```
