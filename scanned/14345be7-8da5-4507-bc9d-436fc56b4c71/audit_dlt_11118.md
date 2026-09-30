# [?] Add comments to tests and use mutex to avoid deadlock

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2021-03-25
Source: https://github.com/matter-labs/zksync/commit/ce4d00f0825fa92de1eabc6b9c0637487effb78d
Type: security-commit

## Details
Add comments to tests and use mutex to avoid deadlock

## Patch
### core/lib/storage/src/tests/chain/block.rs
```diff
@@ -933,6 +933,7 @@ async fn test_operations_counter(mut storage: StorageProcessor<'_>) -> QueryResu
 /// Check that blocks are removed correctly.
 #[db_test]
 async fn test_remove_blocks(mut storage: StorageProcessor<'_>) -> QueryResult<()> {
+    // Insert 5 blocks.
     for block_number in 1..=5 {
         BlockSchema(&mut storage)
             .save_block(gen_sample_block(
@@ -949,9 +950,12 @@ async fn test_remove_blocks(mut storage: StorageProcessor<'_>) -> QueryResult<()
             ))
             .await?;
     }
+    // Remove blocks with numbers greater than 2.
     BlockSchema(&mut storage)
         .remove_blocks(BlockNumber(2))
         .await?;
+
+    // Check if the 2nd block is present, and the 3rd is not.
     assert!(BlockSchema(&mut storage)
         .get_block(BlockNumber(2))
         .await?
@@ -979,6 +983,7 @@ async fn test_remove_pending_block(mut storage: StorageProcessor<'_>) -> QueryRe
         previous_block_root_hash: H256::default(),
         timestamp: 0,
     };
+
     BlockSchema(&mut storage)
         .save_pending_block(pending_block_1.clone())
         .await?;
@@ -991,6 +996,7 @@ async fn test_remove_pending_block(mut storage: StorageProcessor<'_>) -> QueryRe
 /// Check that account tree cache is removed correctly.
 #[db_test]
 async fn test_remove_account_tree_cache(mut storage: StorageProcessor<'_>) -> QueryResult<()> {
+    // Insert account tree cache for 5 blocks.
     for block_number in 1..=5 {
         BlockSchema(&mut storage)
             .save_block(gen_sample_block(
@@ -1004,10 +1010,12 @@ async fn test_remove_account_tree_cache(mut storage: StorageProcessor<'_>) -> Qu
             .await?;
     }
 
+    // Remove account tree cache for blocks with numbers greater than 2.
     BlockSchema(&mut storage)
         .remove_account_tree_cache(BlockNumber(2))
         .await?;
 
+    // Check if account tree cache for the 2nd block is present, and for the 3rd is not.
     assert!(BlockSchema(&mut storage)
         .get_account_tree_cache_block(BlockNumber(2))
         .await?
```

### core/lib/storage/src/tests/chain/mempool.rs
```diff
@@ -352,6 +352,8 @@ async fn contains_and_get_tx(mut storage: StorageProcessor<'_>) -> QueryResult<(
 #[db_test]
 async fn test_return_executed_txs_to_mempool(mut storage: StorageProcessor<'_>) -> QueryResult<()> {
     let txs = gen_transfers(5);
+
+    // Insert 5 executed transactions.
     for block_number in 1..=5 {
         let tx_data = txs.get(block_number - 1).unwrap();
         let executed_tx = NewExecutedTransaction {
@@ -376,26 +378,23 @@ async fn test_return_executed_txs_to_mempool(mut storage: StorageProcessor<'_>)
             .await?;
     }
 
+    // Return txs with block numbers greater than 3 back to mempool.
     MempoolSchema(&mut storage)
         .return_executed_txs_to_mempool(BlockNumber(3))
         .await?;
-    assert_eq!(MempoolSchema(&mut storage).load_txs().await?.len(), 2);
 
+    // Check that the first 3 txs are executed and 2 last are in mempool.
+    assert_eq!(MempoolSchema(&mut storage).load_txs().await?.len(), 2);
     for block_number in 1..=5 {
         let tx_hash = txs.get(block_number - 1).unwrap().hash();
         let tx_in_executed = OperationsSchema(&mut storage)
             .get_executed_operation(tx_hash.as_ref())
             .await?
             .is_some();
-        // let tx_in_mempool = MempoolSchema(&mut storage)
-        //     .get_tx(tx_hash)
-        //     .await?.is_some();
         if block_number <= 3 {
             assert!(tx_in_executed);
-        // assert!(!tx_in_mempool);
         } else {
             assert!(!tx_in_executed);
-            // assert!(tx_in_mempool);
         }
     }
 
```

### core/lib/storage/src/tests/chain/operations.rs
```diff
@@ -376,6 +376,7 @@ async fn remove_rejected_transactions(mut storage: StorageProcessor<'_>) -> Quer
 async fn test_remove_executed_priority_operations(
     mut storage: StorageProcessor<'_>,
 ) -> QueryResult<()> {
+    // Insert 5 priority operations.
     for block_number in 1..=5 {
         let executed_priority_op = NewExecutedPriorityOperation {
             block_number,
@@ -393,9 +394,13 @@ async fn test_remove_executed_priority_operations(
             .store_executed_priority_op(executed_priority_op)
             .await?;
     }
+
+    // Remove priority operation with block numbers greater than 3.
     OperationsSchema(&mut storage)
         .remove_executed_priority_operations(BlockNumber(3))
         .await?;
+
+    // Check that priority operation from the 3rd block is present and from the 4th is not.
     let block3_txs = BlockSchema(&mut storage)
         .get_block_transactions(BlockNumber(3))
         .await?;
```

### core/lib/storage/src/tests/chain/state.rs
```diff
@@ -228,6 +228,7 @@ async fn test_remove_account_updates(mut storage: StorageProcessor<'_>) -> Query
     let (_accounts_block_3, updates_block_3) =
         apply_random_updates(accounts_block_2.clone(), &mut rng);
 
+    // Commit updates for 3 blocks.
     StateSchema(&mut storage)
         .commit_state_update(BlockNumber(1), &updates_block_1, 0)
         .await?;
@@ -238,6 +239,7 @@ async fn test_remove_account_updates(mut storage: StorageProcessor<'_>) -> Query
         .commit_state_update(BlockNumber(3), &updates_block_3, 0)
         .await?;
 
+    // Remove updates for blocks with number greater than 2.
     StateSchema(&mut storage)
         .remove_account_balance_updates(BlockNumber(2))
         .await?;
@@ -257,6 +259,8 @@ async fn test_remove_account_updates(mut storage: StorageProcessor<'_>) -> Query
     let diff3 = StateSchema(&mut storage)
         .load_state_diff(BlockNumber(0), Some(BlockNumber(3)))
         .await?;
+
+    // Check that there are updates for the 2nd block and there are not for the 3rd by comparing diffs.
     assert_ne!(diff1, diff2);
     assert_eq!(diff2, diff3);
     Ok(())
```

### core/lib/storage/src/tests/ethereum.rs
```diff
@@ -394,6 +394,8 @@ async fn ethereum_gas_update(mut storage: StorageProcessor<'_>) -> QueryResult<(
 #[db_test]
 async fn test_update_eth_parameters(mut storage: StorageProcessor<'_>) -> QueryResult<()> {
     storage.ethereum_schema().initialize_eth_data().await?;
+
+    // Updates eth parameters and checks if they were really saved.
     storage
         .ethereum_schema()
         .update_eth_parameters(BlockNumber(5), Nonce(3))
```

### core/lib/storage/src/tests/prover.rs
```diff
@@ -6,9 +6,18 @@ use zksync_types::prover::{ProverJob, ProverJobType};
 use crate::test_data::{gen_sample_block, get_sample_aggregated_proof, get_sample_single_proof};
 use crate::tests::db_test;
 use crate::{prover::ProverSchema, QueryResult, StorageProcessor};
+use lazy_static::lazy_static;
+use std::sync::Mutex;
 use zksync_types::BlockNumber;
 
+lazy_static! {
+    static ref MUTEX: Mutex<()> = Mutex::new(());
+}
+
 async fn get_idle_job_from_queue(mut storage: &mut StorageProcessor<'_>) -> QueryResult<ProverJob> {
+    // Lock to prevent database deadlock
+    let _lock = MUTEX.lock().unwrap();
+
     let job = ProverSchema(&mut storage)
         .get_idle_prover_job_from_job_queue()
         .await?;
@@ -267,6 +276,7 @@ async fn test_store_witness(mut storage: StorageProcessor<'_>) -> QueryResult<()
 /// Checks that block witnesses are removed correctly.
 #[db_test]
 async fn test_remove_witnesses(mut storage: StorageProcessor<'_>) -> QueryResult<()> {
+    // Insert 5 blocks and witnesses for them.
     for block_number in 1..=5 {
         storage
             .chain()
@@ -283,16 +293,18 @@ async fn test_remove_witnesses(mut storage: StorageProcessor<'_>) -> QueryResult
             .store_witness(BlockNumber(block_number), witness)
             .await?;
     }
+    // Remove witnesses for the 4th and 5th blocks.
     storage
         .prover_schema()
         .remove_witnesses(BlockNumber(3))
         .await?;
+
+    // Check that there is a witness for the 3rd block and no witness for the 4th.
     assert!(storage
         .prover_schema()
         .get_witness(BlockNumber(3))
         .await?
         .is_some());
-
     assert!(storage
         .prover_schema()
         .get_witness(BlockNumber(4))
@@ -302,90 +314,99 @@ async fn test_remove_witnesses(mut storage: StorageProcessor<'_>) -> QueryResult
     Ok(())
 }
 
-// /// Checks that block proofs are removed correctly.
-// #[db_test]
-// async fn test_remove_proofs(mut storage: StorageProcessor<'_>) -> QueryResult<()> {
-//     let proof = get_sample_single_proof();
-//     let job_data = serde_json::Value::default();
-//     for block_number in 1..=5 {
-//         ProverSchema(&mut storage)
-//             .add_prover_job_to_job_queue(
-//                 BlockNumber(block_number),
-//                 BlockNumber(block_number),
-//                 job_data.clone(),
-//                 0,
-//                 ProverJobType::SingleProof,
-//             )
-//             .await?;
-//         let job_id = get_idle_job_from_queue(&mut storage).await?.job_id;
-//         ProverSchema(&mut storage)
-//             .store_proof(job_id, BlockNumber(block_number), &proof)
-//             .await?;
-//     }
-
-//     ProverSchema(&mut storage)
-//         .remove_proofs(BlockNumber(3))
-//         .await?;
-
-//     assert!(ProverSchema(&mut storage)
-//         .load_proof(BlockNumber(3))
-//         .await?
-//         .is_some());
-//     assert!(ProverSchema(&mut storage)
-//         .load_proof(BlockNumber(4))
-//         .await?
-//         .is_none());
-
-//     let aggregated_proof = get_sample_aggregated_proof();
-
-//     ProverSchema(&mut storage)
-//         .add_prover_job_to_job_queue(
-//             BlockNumber(1),
-//             BlockNumber(2),
-//             job_data.clone(),
-//             1,
-//             ProverJobType::AggregatedProof,
-//         )
-//         .await?;
-//     let job_id = get_idle_job_from_queue(&mut storage).await?.job_id;
-//     ProverSchema(&mut storage)
-//         .store_aggregated_proof(job_id, BlockNumber(1), BlockNumber(2), &aggregated_proof)
-//         .await?;
-
-//     ProverSchema(&mut storage)
-//         .add_prover_job_to_job_queue(
-//             BlockNumber(3),
-//             BlockNumber(5),
-//             job_data.clone(),
-//             1,
-//             ProverJobType::AggregatedProof,
-//         )
-//         .await?;
-//     let job_id = get_idle_job_from_queue(&mut storage).await?.job_id;
-//     ProverSchema(&mut storage)
-//         .store_aggregated_proof(job_id, BlockNumber(3), BlockNumber(5), &aggregated_proof)
-//         .await?;
-
-//     ProverSchema(&mut storage)
-//         .remove_aggregated_proofs(BlockNumber(3))
-//         .await?;
-
-//     assert!(ProverSchema(&mut storage)
-//         .load_aggregated_proof(BlockNumber(1), BlockNumber(2))
-//         .await?
-//         .is_some());
-//     assert!(ProverSchema(&mut storage)
-//         .load_aggregated_proof(BlockNumber(3), BlockNumber(5))
-//         .await?
-//         .is_none());
-
-//     Ok(())
-// }
+/// Checks that block proofs are removed correctly.
+#[db_test]
+async fn test_remove_proofs(mut storage: StorageProcessor<'_>) -> QueryResult<()> {
+    let proof = get_sample_single_proof();
+    let job_data = serde_json::Value::default();
+
+    // Insert proofs for 5 blocks.
+    for block_number in 1..=5 {
+        ProverSchema(&mut storage)
+            .add_prover_job_to_job_queue(
+                BlockNumber(block_number),
+                BlockNumber(block_number),
+                job_data.clone(),
+                0,
+                ProverJobType::SingleProof,
+            )
+            .await?;
+        let job_id = get_idle_job_from_queue(&mut storage).await?.job_id;
+        ProverSchema(&mut storage)
+            .store_proof(job_id, BlockNumber(block_number), &proof)
+            .await?;
+    }
+
+    // Remove proofs for the 4th and 5th blocks.
+    ProverSchema(&mut storage)
+        .remove_proofs(BlockNumber(3))
+        .await?;
+
+    // Check that there is a proof for the 3rd block and no proof for the 4th.
+    assert!(ProverSchema(&mut storage)
+        .load_proof(BlockNumber(3))
+        .await?
+        .is_some());
+    assert!(ProverSchema(&mut storage)
+        .load_proof(BlockNumber(4))
+        .await?
+        .is_none());
+
+    let aggregated_proof = get_sample_aggregated_proof();
+
+    // Insert arregated proofs for 1-2 blocks and 3-5 blocks.
+    ProverSchema(&mut storage)
+        .add_prover_job_to_job_queue(
+            BlockNumber(1),
+            BlockNumber(2),
+            job_data.clone(),
+            1,
+            ProverJobType::AggregatedProof,
+        )
+        .await?;
+    let job_id = get_idle_job_from_queue(&mut storage).await?.job_id;
+    ProverSchema(&mut storage)
+        .store_aggregated_proof(job_id, BlockNumber(1), BlockNumber(2), &aggregated_proof)
+        .await?;
+
+    ProverSchema(&mut storage)
+        .add_prover_job_to_job_queue(
+            BlockNumber(3),
+            BlockNumber(5),
+            job_data.clone(),
+            1,
+            ProverJobType::AggregatedProof,
+        )
+        .await?;
+    let job_id = get_idle_job_from_queue(&mut storage).await?.job_id;
+    ProverSchema(&mut storage)
+        .store_aggregated_proof(job_id, BlockNumber(3), BlockNumber(5), &aggregated_proof)
+        .await?;
+
+    // Remove aggregated proofs for blocks with numbers greater than 3. It means that proof for 3-5 blocks should be deleted.
+    ProverSchema(&mut storage)
+        .remove_aggregated_proofs(BlockNumber(3))
+        .await?;
+
+    // Check that proof 1-2 is present and 3-5 is not.
+    assert!(ProverSchema(&mut storage)
+        .load_aggregated_proof(BlockNumber(1), BlockNumber(2))
+        .await?
+        .is_some());
+    assert!(ProverSchema(&mut storage)
+        .load_aggregated_proof(BlockNumber(3), BlockNumber(5))
+        .await?
+        .is_none());
+
+    Ok(())
+}
 
 /// Checks that prover jobs are removed correctly.
 #[db_test]
 async fn test_remove_prover_jobs(mut storage: StorageProcessor<'_>) -> QueryResult<()> {
     let job_data = serde_json::Value::default();
+
+    // Insert jobs for blocks 1-3 and 4-5.
     ProverSchema(&mut storage)
         .add_prover_job_to_job_queue(
             BlockNumber(1),
@@ -405,6 +426,7 @@ async fn test_remove_prover_jobs(mut storage: StorageProcessor<'_>) -> QueryResu
         )
         .await?;
 
+    // Remove prover_jobs for blocks with numbers greater than 2. After that only one job for 1-2 blocks should left.
     ProverSchema(&mut storage)
         .remove_prover_jobs(BlockNumber(2))
         .await?;
```
