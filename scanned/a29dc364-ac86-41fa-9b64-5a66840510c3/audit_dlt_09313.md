# [?] fix(anvil): prevent panic in ots (#8835)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-09-10
Source: https://github.com/foundry-rs/foundry/commit/be451fb93a0d0ec52152fb67cc6c36cd8fbd7ae1
Type: security-commit

## Details
fix(anvil): prevent panic in ots (#8835)

* fix(anvil): prevent panic in ots

* fix(anvil): use block_by_number in ots_block_tx & ots_search_transactions

* nit

* nit

## Patch
### crates/anvil/src/eth/otterscan/api.rs
```diff
@@ -419,20 +419,19 @@ impl EthApi {
 
         let receipt_futs = block.transactions.hashes().map(|hash| self.transaction_receipt(hash));
 
-        let receipts = join_all(receipt_futs)
-            .await
-            .into_iter()
-            .map(|r| match r {
-                Ok(Some(r)) => {
-                    let timestamp =
-                        self.backend.get_block(r.block_number.unwrap()).unwrap().header.timestamp;
-                    let receipt = r.map_inner(OtsReceipt::from);
-                    let res = OtsTransactionReceipt { receipt, timestamp: Some(timestamp) };
-                    Ok(res)
-                }
-                _ => Err(BlockchainError::DataUnavailable),
-            })
-            .collect::<Result<Vec<_>>>()?;
+        let receipts = join_all(receipt_futs.map(|r| async {
+            if let Ok(Some(r)) = r.await {
+                let block = self.block_by_number(r.block_number.unwrap().into()).await?;
+                let timestamp = block.ok_or(BlockchainError::BlockNotFound)?.header.timestamp;
+                let receipt = r.map_inner(OtsReceipt::from);
+                Ok(OtsTransactionReceipt { receipt, timestamp: Some(timestamp) })
+            } else {
+                Err(BlockchainError::BlockNotFound)
+            }
+        }))
+        .await
+        .into_iter()
+        .collect::<Result<Vec<_>>>()?;
 
         let transaction_count = block.transactions().len();
         let fullblock = OtsBlock { block: block.inner, transaction_count };
@@ -458,23 +457,18 @@ impl EthApi {
                 Ok(Some(t)) => Ok(t.inner),
                 _ => Err(BlockchainError::DataUnavailable),
             })
-            .collect::<Result<_>>()?;
-
-        let receipts = join_all(hashes.iter().map(|hash| async {
-            match self.transaction_receipt(*hash).await {
-                Ok(Some(receipt)) => {
-                    let timestamp = self
-                        .backend
-                        .get_block(receipt.block_number.unwrap())
-                        .unwrap()
-                        .header
-                        .timestamp;
-                    let receipt = receipt.map_inner(OtsReceipt::from);
-                    let res = OtsTransactionReceipt { receipt, timestamp: Some(timestamp) };
-                    Ok(res)
-                }
-                Ok(None) => Err(BlockchainError::DataUnavailable),
-                Err(e) => Err(e),
+            .collect::<Result<Vec<_>>>()?;
+
+        let receipt_futs = hashes.iter().map(|hash| self.transaction_receipt(*hash));
+
+        let receipts = join_all(receipt_futs.map(|r| async {
+            if let Ok(Some(r)) = r.await {
+                let block = self.block_by_number(r.block_number.unwrap().into()).await?;
+                let timestamp = block.ok_or(BlockchainError::BlockNotFound)?.header.timestamp;
+                let receipt = r.map_inner(OtsReceipt::from);
+                Ok(OtsTransactionReceipt { receipt, timestamp: Some(timestamp) })
+            } else {
+                Err(BlockchainError::BlockNotFound)
             }
         }))
         .await
```
