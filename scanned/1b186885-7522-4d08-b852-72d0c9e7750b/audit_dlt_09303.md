# [?] fix(`anvil`): unwrap panic in `eth/backend/mem/mod.rs` (#11141)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-07-29
Source: https://github.com/foundry-rs/foundry/commit/54d256113bd5ecdc284ee43a5aa968c20b1eb28e
Type: security-commit

## Details
fix(`anvil`): unwrap panic in `eth/backend/mem/mod.rs` (#11141)

make typed request casting not panic and return useful error to user

## Patch
### crates/anvil/src/eth/backend/mem/mod.rs
```diff
@@ -1722,11 +1722,10 @@ impl Backend {
                     cache_db.commit(state);
                     gas_used += result.gas_used();
 
-                    // TODO: this is likely incomplete
                     // create the transaction from a request
                     let from = request.from.unwrap_or_default();
-                    let request =
-                        transaction_request_to_typed(WithOtherFields::new(request)).unwrap();
+                    let request = transaction_request_to_typed(WithOtherFields::new(request))
+                        .ok_or(BlockchainError::MissingRequiredFields)?;
                     let tx = build_typed_transaction(
                         request,
                         Signature::new(Default::default(), Default::default(), false),
```

### crates/anvil/src/eth/error.rs
```diff
@@ -115,6 +115,8 @@ pub enum BlockchainError {
         /// Duration that was waited before timing out
         duration: Duration,
     },
+    #[error("Failed to parse transaction request: missing required fields")]
+    MissingRequiredFields,
 }
 
 impl From<eyre::Report> for BlockchainError {
@@ -563,6 +565,9 @@ impl<T: Serialize> ToRpcResponseResult for Result<T> {
                 err @ BlockchainError::UnknownTransactionType => {
                     RpcError::invalid_params(err.to_string())
                 }
+                err @ BlockchainError::MissingRequiredFields => {
+                    RpcError::invalid_params(err.to_string())
+                }
             }
             .into(),
         }
```
