# [?] fix: blob hashes panic for opstack (#565)

## Summary
Severity: Unknown
Chain: Light client
Component: a16z/helios
Published: 2025-03-21
Source: https://github.com/a16z/helios/commit/4102e41a10df8821f8474ced262cd7d26a5a8e67
Type: security-commit

## Details
fix: blob hashes panic for opstack (#565)

## Patch
### opstack/src/spec.rs
```diff
@@ -1,7 +1,7 @@
 use alloy::{
     consensus::{
         proofs::{calculate_transaction_root, calculate_withdrawals_root},
-        BlockHeader, Receipt, ReceiptWithBloom, Transaction as TxTrait, TxReceipt, TxType,
+        BlockHeader, Receipt, ReceiptWithBloom, TxReceipt, TxType,
     },
     primitives::{Address, Bytes, ChainId, TxKind, U256},
     rpc::types::{AccessList, Log, TransactionRequest},
@@ -139,10 +139,8 @@ impl NetworkSpec for OpStack {
                 <OpTransactionRequest as TransactionBuilder<Self>>::max_fee_per_gas(tx)
                     .map(U256::from),
             blob_hashes: tx
-                .clone()
-                .build_typed_tx()
-                .unwrap()
-                .blob_versioned_hashes()
+                .as_ref()
+                .blob_versioned_hashes
                 .as_ref()
                 .map(|v| v.to_vec())
                 .unwrap_or_default(),
```
