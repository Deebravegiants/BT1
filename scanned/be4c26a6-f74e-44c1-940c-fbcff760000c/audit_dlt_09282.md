# [?] fix(anvil): avoid blob tx stack overflow (#16486)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-08-31
Source: https://github.com/foundry-rs/foundry/commit/d3083c3ad47f09de8154616ec27781a2353f7d26
Type: security-commit

## Details
fix(anvil): avoid blob tx stack overflow (#16486)

Decode pooled EIP-4844 transactions outside the RPC worker stack while preserving the inline path for other transaction types.

## Patch
### .changelog/anvil-blob-transaction-stack-overflow.md
```diff
@@ -0,0 +1,5 @@
+---
+anvil: patch
+---
+
+Fixed a stack overflow when submitting signed EIP-4844 blob transactions.
```

### crates/anvil/src/eth/api.rs
```diff
@@ -41,7 +41,7 @@ use alloy_consensus::{
 };
 use alloy_dyn_abi::TypedData;
 use alloy_eips::{
-    eip2718::Encodable2718,
+    eip2718::{EIP4844_TX_TYPE_ID, Encodable2718},
     eip7910::{EthConfig, EthForkConfig},
 };
 use alloy_evm::overrides::{OverrideBlockHashes, apply_state_overrides};
@@ -2944,11 +2944,21 @@ impl EthApi<FoundryNetwork> {
         } else {
             None
         };
-        let raw = service_encoded.as_deref().unwrap_or(tx.as_ref());
+        let raw = service_encoded.map(Bytes::from).unwrap_or(tx);
 
-        let mut data = raw;
-        let transaction = FoundryTxEnvelope::decode_2718(&mut data)
-            .map_err(|_| BlockchainError::FailedToDecodeSignedTransaction)?;
+        let transaction = if raw.first() == Some(&EIP4844_TX_TYPE_ID) {
+            // Pooled EIP-4844 decoding uses large stack frames for inline blobs. Isolate it from
+            // the already-large RPC dispatcher without increasing every worker's stack.
+            let raw = raw.clone();
+            tokio::task::spawn_blocking(move || FoundryTxEnvelope::decode_2718(&mut raw.as_ref()))
+                .await
+                .map_err(|_| {
+                    BlockchainError::Internal("transaction decoding task panicked".into())
+                })?
+        } else {
+            FoundryTxEnvelope::decode_2718(&mut raw.as_ref())
+        }
+        .map_err(|_| BlockchainError::FailedToDecodeSignedTransaction)?;
 
         self.ensure_typed_transaction_supported(&transaction)?;
 
@@ -2963,7 +2973,7 @@ impl EthApi<FoundryNetwork> {
         };
 
         if self.backend.is_tempo() && TempoHardfork::from(self.backend.hardfork()).is_t5() {
-            let classification = classify_payment_lane(raw);
+            let classification = classify_payment_lane(raw.as_ref());
             trace!(target: "node", tx = ?transaction.hash(), ?classification, "classified transaction lane");
         }
 
```

### crates/anvil/tests/it/eip4844.rs
```diff
@@ -4,7 +4,7 @@ use alloy_consensus::{
     TxEip4844, proofs::calculate_transaction_root,
 };
 use alloy_eips::{
-    Decodable2718, Typed2718,
+    eip2718::{Decodable2718, EIP4844_TX_TYPE_ID, Typed2718},
     eip4844::{
         BLOB_TX_MIN_BLOB_GASPRICE, DATA_GAS_PER_BLOB, MAX_DATA_GAS_PER_BLOCK_DENCUN,
         TARGET_DATA_GAS_PER_BLOCK_DENCUN,
@@ -418,6 +418,16 @@ async fn can_correctly_estimate_blob_gas_with_recommended_fillers_with_signer()
     );
 }
 
+#[tokio::test(flavor = "multi_thread")]
+async fn rejects_malformed_eip4844_transaction() {
+    let node_config = NodeConfig::test().with_hardfork(Some(EthereumHardfork::Cancun.into()));
+    let (_api, handle) = spawn(node_config).await;
+
+    let err = handle.http_provider().send_raw_transaction(&[EIP4844_TX_TYPE_ID]).await.unwrap_err();
+
+    assert!(err.to_string().contains("Failed to decode transaction"));
+}
+
 // <https://github.com/foundry-rs/foundry/issues/9924>
 #[tokio::test]
 async fn can_bypass_sidecar_requirement() {
```
