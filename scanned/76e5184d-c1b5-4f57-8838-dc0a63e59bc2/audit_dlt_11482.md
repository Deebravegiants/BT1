# [?] fix: return an error instead of panicking on a receipt or tx without an index (#810)

## Summary
Severity: Unknown
Chain: Light client
Component: a16z/helios
Published: 2026-09-14
Source: https://github.com/a16z/helios/commit/d20aa4f4de5886b6c78004447ee197a1cf744362
Type: security-commit

## Details
fix: return an error instead of panicking on a receipt or tx without an index (#810)

verify_receipt_proof and verify_transaction_proof unwrapped
transaction_index(), which is None for anything not included in a block.
Both are called on responses straight from a verifiable-api server, before
that server's data has been proven, so a response carrying
"transactionIndex": null aborts the process — release builds use
panic = "abort".

get_transaction_by_location already handles the same Option with ok_or;
the other two call sites did not. Return ExecutionError::TransactionNotIncluded
instead so the response is rejected like any other invalid one.

## Patch
### core/src/execution/errors.rs
```diff
@@ -21,6 +21,8 @@ pub enum ExecutionError {
     MissingLog(B256, U256),
     #[error("too many logs to prove: {0} spanning {1} blocks current limit is: {2} blocks")]
     TooManyLogsToProve(usize, usize, usize),
+    #[error("transaction {0} is not included in a block")]
+    TransactionNotIncluded(B256),
     #[error("execution rpc is for the incorrect network")]
     IncorrectRpcNetwork(),
     #[error("block not found: {0}")]
```

### core/src/execution/proof.rs
```diff
@@ -143,7 +143,11 @@ pub fn verify_receipt_proof<N: NetworkSpec>(
     proof: &[Bytes],
 ) -> Result<()> {
     let key = {
-        let index = receipt.transaction_index().unwrap() as usize;
+        let index = receipt
+            .transaction_index()
+            .ok_or(ExecutionError::TransactionNotIncluded(
+                receipt.transaction_hash(),
+            ))? as usize;
         let index_buffer = rlp::encode_fixed_size(&index);
         Nibbles::unpack(&index_buffer)
     };
@@ -190,7 +194,9 @@ pub fn verify_transaction_proof<N: NetworkSpec>(
     proof: &[Bytes],
 ) -> Result<()> {
     let key = {
-        let index = tx.transaction_index().unwrap() as usize;
+        let index =
+            tx.transaction_index()
+                .ok_or(ExecutionError::TransactionNotIncluded(tx.tx_hash()))? as usize;
         let index_buffer = rlp::encode_fixed_size(&index);
         Nibbles::unpack(&index_buffer)
     };
@@ -317,6 +323,29 @@ mod tests {
         }
     }
 
+    #[test]
+    fn test_verify_receipt_proof_without_transaction_index() {
+        // A receipt that is not included in a block carries no index. Verification
+        // must reject it rather than panic, since the receipt comes from a server
+        // whose responses are exactly what this proof is meant to check.
+        let mut receipt = rpc_tx_receipt();
+        receipt.transaction_index = None;
+
+        let result = verify_receipt_proof::<EthereumSpec>(&receipt, B256::ZERO, &[]);
+
+        assert!(result.is_err());
+    }
+
+    #[test]
+    fn test_verify_transaction_proof_without_transaction_index() {
+        let mut tx = rpc_tx();
+        tx.transaction_index = None;
+
+        let result = verify_transaction_proof::<EthereumSpec>(&tx, B256::ZERO, &[]);
+
+        assert!(result.is_err());
+    }
+
     #[test]
     fn test_verify_block_receipts() {
         let receipts = rpc_block_receipts();
```
