# [?] fix: return an error instead of panic for missing transactions validation storage proof (#10652)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-02-26
Source: https://github.com/near/nearcore/commit/8ef51b01565a077678b4e8dfa2d2c2e74b605c97
Type: security-commit

## Details
fix: return an error instead of panic for missing transactions validation storage proof (#10652)

To be consistent with how we handle missing state transition data for
applying chunks:
```
            let StoredChunkStateTransitionData { base_state, receipts_hash } = store
                .get_ser(
                    near_store::DBCol::StateTransitionData,
                    &near_primitives::utils::get_block_shard_id(main_block, shard_id),
                )?
                .ok_or(Error::Other(format!(
                    "Missing main transition state proof for block {main_block} and shard {shard_id}"
                )))?;
```

## Patch
### chain/client/src/stateless_validation/state_witness_producer.rs
```diff
@@ -99,8 +99,11 @@ impl Client {
         let new_transactions_validation_state = if new_transactions.is_empty() {
             PartialState::default()
         } else {
-            // With stateless validation chunk producer uses recording reads when validating transactions. The storage proof must be available here.
-            transactions_storage_proof.expect("Missing storage proof for transactions validation")
+            // With stateless validation chunk producer uses recording reads when validating transactions.
+            // The storage proof must be available here.
+            transactions_storage_proof.ok_or_else(|| {
+                Error::Other("Missing storage proof for transactions validation".to_owned())
+            })?
         };
 
         let source_receipt_proofs =
```
