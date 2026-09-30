# [?] fix: potential race condition in testing

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-03-05
Source: https://github.com/fedimint/fedimint/commit/0275f0bae9fe3b63af816f6222dae11f52d1cf7c
Type: security-commit

## Details
fix: potential race condition in testing

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### modules/fedimint-walletv2-client/src/lib.rs
```diff
@@ -546,25 +546,6 @@ impl WalletClientModule {
                     .await?
                     .ok_or(anyhow!("No consensus feerate is available"))?;
 
-                if tx_out.value > receive_fee && !deposit_range.spent.contains(&deposit_index) {
-                    // In order to not overpay on fees we choose to wait, the congestion will clear
-                    // up within a few blocks.
-                    if self.module_api.pending_tx_chain().await?.len() >= 3 {
-                        return Ok(false);
-                    }
-
-                    let (operation_id, txid) = self
-                        .receive_deposit(deposit_index, tx_out.value, address_index, receive_fee)
-                        .await;
-
-                    self.client_ctx
-                        .transaction_updates(operation_id)
-                        .await
-                        .await_tx_accepted(txid)
-                        .await
-                        .map_err(|e| anyhow!("Claim transaction for deposit was rejected: {e}"))?;
-                }
-
                 let next_address_index = valid_indices
                     .last()
                     .copied()
@@ -584,6 +565,25 @@ impl WalletClientModule {
 
                     address_map.insert(self.derive_address(index).script_pubkey(), index);
                 }
+
+                if tx_out.value > receive_fee && !deposit_range.spent.contains(&deposit_index) {
+                    // In order to not overpay on fees we choose to wait, the congestion will clear
+                    // up within a few blocks.
+                    if self.module_api.pending_tx_chain().await?.len() >= 3 {
+                        return Ok(false);
+                    }
+
+                    let (operation_id, txid) = self
+                        .receive_deposit(deposit_index, tx_out.value, address_index, receive_fee)
+                        .await;
+
+                    self.client_ctx
+                        .transaction_updates(operation_id)
+                        .await
+                        .await_tx_accepted(txid)
+                        .await
+                        .map_err(|e| anyhow!("Claim transaction for deposit was rejected: {e}"))?;
+                }
             }
 
             let mut dbtx = self.db.begin_transaction().await;
```
