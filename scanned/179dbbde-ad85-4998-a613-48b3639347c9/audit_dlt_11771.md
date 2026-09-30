# [?] Abort transactions that attempt to double-spend inputs

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2023-12-04
Source: https://github.com/AleoNet/snarkVM-test/commit/d9bb326bbdc577345caf8babb8752f91dc765d75
Type: security-commit

## Details
Abort transactions that attempt to double-spend inputs

## Patch
### synthesizer/src/vm/finalize.rs
```diff
@@ -214,6 +214,8 @@ impl<N: Network, C: ConsensusStorage<N>> VM<N, C> {
             let mut aborted = Vec::new();
             // Initialize a counter for the confirmed transaction index.
             let mut counter = 0u32;
+            // Initialize a list of spent input IDs.
+            let mut input_ids: IndexSet<Field<N>> = IndexSet::new();
 
             // Finalize the transactions.
             'outer: for transaction in transactions {
@@ -226,6 +228,19 @@ impl<N: Network, C: ConsensusStorage<N>> VM<N, C> {
                     continue 'outer;
                 }
 
+                // TODO (raychu86): Consider using InputStore with contains_input_id_speculative instead.
+                //  This can be added to the `finalize_execution` and `finalize_fee` methods to allow for
+                //  a possible rejected transaction instead of always aborting.
+                // Ensure that the transaction is not double-spending an input.
+                for input_id in transaction.input_ids() {
+                    if input_ids.contains(input_id) {
+                        // Store the aborted transaction.
+                        aborted.push((transaction.clone(), format!("Double-spending input {input_id}")));
+                        // Continue to the next transaction.
+                        continue 'outer;
+                    }
+                }
+
                 // Process the transaction in an isolated atomic batch.
                 // - If the transaction succeeds, the finalize operations are stored.
                 // - If the transaction fails, the atomic batch is aborted and no finalize operations are stored.
@@ -314,6 +329,9 @@ impl<N: Network, C: ConsensusStorage<N>> VM<N, C> {
                 match outcome {
                     // If the transaction succeeded, store it and continue to the next transaction.
                     Ok(confirmed_transaction) => {
+                        // Add the input IDs to the set of spent input IDs.
+                        input_ids.extend(confirmed_transaction.transaction().input_ids());
+                        // Store the confirmed transaction.
                         confirmed.push(confirmed_transaction);
                         // Increment the transaction index counter.
                         counter = counter.saturating_add(1);
```

### synthesizer/src/vm/mod.rs
```diff
@@ -59,7 +59,7 @@ use synthesizer_process::{Authorization, Process, Trace};
 use synthesizer_program::{FinalizeGlobalState, FinalizeOperation, FinalizeStoreTrait, Program};
 
 use aleo_std::prelude::{finish, lap, timer};
-use indexmap::IndexMap;
+use indexmap::{IndexMap, IndexSet};
 use parking_lot::RwLock;
 use std::sync::Arc;
 
```
