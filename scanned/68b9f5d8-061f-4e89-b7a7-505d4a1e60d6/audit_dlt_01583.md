# [?] Fix - overflow in `test_serialize_parameters_with_many_accounts()` (#7599)

## Summary
Severity: Unknown
Chain: Solana
Component: jito-foundation/jito-solana
Published: 2025-08-22
Source: https://github.com/jito-foundation/jito-solana/commit/83d40ef2be8ed0a63bbf9346d3746006da4778c5
Type: security-commit

## Details
Fix - overflow in `test_serialize_parameters_with_many_accounts()` (#7599)

* Adds back the debug_assert!() in TransactionContext::configure_next_instruction_for_tests().

* Adjusts test_serialize_parameters_with_many_accounts() to avoid the overflow.

* Uses MAX_ACCOUNTS_PER_TRANSACTION for dedep_map len.

## Patch
### program-runtime/src/serialization.rs
```diff
@@ -665,7 +665,9 @@ mod tests {
         solana_sbpf::{memory_region::MemoryMapping, program::SBPFVersion, vm::Config},
         solana_sdk_ids::bpf_loader,
         solana_system_interface::MAX_PERMITTED_ACCOUNTS_DATA_ALLOCATIONS_PER_TRANSACTION,
-        solana_transaction_context::{InstructionAccount, TransactionContext},
+        solana_transaction_context::{
+            InstructionAccount, TransactionContext, MAX_ACCOUNTS_PER_TRANSACTION,
+        },
         std::{
             cell::RefCell,
             mem::transmute,
@@ -764,14 +766,30 @@ mod tests {
                     transaction_context,
                     transaction_accounts
                 );
-                invoke_context
-                    .transaction_context
-                    .configure_next_instruction_for_tests(
-                        0,
-                        instruction_accounts,
-                        &instruction_data,
-                    )
-                    .unwrap();
+                if instruction_accounts.len() > MAX_ACCOUNTS_PER_INSTRUCTION {
+                    // Special case implementation of configure_next_instruction_for_tests()
+                    // which avoids the overflow when constructing the dedup_map
+                    // by simply not filling it.
+                    let dedup_map = vec![u8::MAX; MAX_ACCOUNTS_PER_TRANSACTION];
+                    invoke_context
+                        .transaction_context
+                        .configure_next_instruction(
+                            0,
+                            instruction_accounts,
+                            dedup_map,
+                            &instruction_data,
+                        )
+                        .unwrap();
+                } else {
+                    invoke_context
+                        .transaction_context
+                        .configure_next_instruction_for_tests(
+                            0,
+                            instruction_accounts,
+                            &instruction_data,
+                        )
+                        .unwrap();
+                }
                 invoke_context.push().unwrap();
                 let instruction_context = invoke_context
                     .transaction_context
```

### transaction-context/src/lib.rs
```diff
@@ -398,6 +398,7 @@ impl TransactionContext {
         instruction_accounts: Vec<InstructionAccount>,
         instruction_data: &[u8],
     ) -> Result<(), InstructionError> {
+        debug_assert!(instruction_accounts.len() <= u8::MAX as usize);
         let mut dedup_map = vec![u8::MAX; MAX_ACCOUNTS_PER_TRANSACTION];
         for (idx, account) in instruction_accounts.iter().enumerate() {
             let index_in_instruction = dedup_map
```
