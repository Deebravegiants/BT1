# [?] Fix CGC backfill race condition (#8267)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-11-03
Source: https://github.com/sigp/lighthouse/commit/b57d046c4ad9cf60a8053c4c43ea99e4b326bc01
Type: security-commit

## Details
Fix CGC backfill race condition (#8267)

During custody backfill sync there could be an edge case where we update CGC at the same time where we are importing a batch of columns which may cause us to incorrectly overwrite values when calling `backfill_validator_custody_requirements`. To prevent this race condition, the expected cgc is now passed into this function and is used to check if the expected cgc == the current validator cgc. If the values arent equal, this probably indicates that a very recent CGC occurred so we do not prune/update values in the `epoch_validator_custody_requirements` map.


  


Co-Authored-By: Eitan Seri-Levi <eserilev@ucsc.edu>

## Patch
### beacon_node/beacon_chain/src/custody_context.rs
```diff
@@ -134,8 +134,17 @@ impl ValidatorRegistrations {
     ///
     /// This is done by pruning all values on/after `effective_epoch` and updating the map to store
     /// the latest validator custody requirements for the `effective_epoch`.
-    pub fn backfill_validator_custody_requirements(&mut self, effective_epoch: Epoch) {
+    pub fn backfill_validator_custody_requirements(
+        &mut self,
+        effective_epoch: Epoch,
+        expected_cgc: u64,
+    ) {
         if let Some(latest_validator_custody) = self.latest_validator_custody_requirement() {
+            // If the expected cgc isn't equal to the latest validator custody a very recent cgc change may have occurred.
+            // We should not update the mapping.
+            if expected_cgc != latest_validator_custody {
+                return;
+            }
             // Delete records if
             // 1. The epoch is greater than or equal than `effective_epoch`
             // 2. the cgc requirements match the latest validator custody requirements
@@ -517,10 +526,14 @@ impl<E: EthSpec> CustodyContext<E> {
 
     /// The node has completed backfill for this epoch. Update the internal records so the function
     /// [`Self::custody_columns_for_epoch()`] returns up-to-date results.
-    pub fn update_and_backfill_custody_count_at_epoch(&self, effective_epoch: Epoch) {
+    pub fn update_and_backfill_custody_count_at_epoch(
+        &self,
+        effective_epoch: Epoch,
+        expected_cgc: u64,
+    ) {
         self.validator_registrations
             .write()
-            .backfill_validator_custody_requirements(effective_epoch);
+            .backfill_validator_custody_requirements(effective_epoch, expected_cgc);
     }
 }
 
@@ -604,11 +617,13 @@ mod tests {
         custody_context: &CustodyContext<E>,
         start_epoch: Epoch,
         end_epoch: Epoch,
+        expected_cgc: u64,
     ) {
         assert!(start_epoch >= end_epoch);
         // Call from end_epoch down to start_epoch (inclusive), simulating backfill
         for epoch in (end_epoch.as_u64()..=start_epoch.as_u64()).rev() {
-            custody_context.update_and_backfill_custody_count_at_epoch(Epoch::new(epoch));
+            custody_context
+                .update_and_backfill_custody_count_at_epoch(Epoch::new(epoch), expected_cgc);
         }
     }
 
@@ -1368,7 +1383,7 @@ mod tests {
         );
 
         // Backfill from epoch 20 down to 15 (simulating backfill)
-        complete_backfill_for_epochs(&custody_context, head_epoch, Epoch::new(15));
+        complete_backfill_for_epochs(&custody_context, head_epoch, Epoch::new(15), final_cgc);
 
         // After backfilling to epoch 15, it should use latest CGC (32)
         assert_eq!(
@@ -1406,7 +1421,43 @@ mod tests {
         let custody_context = setup_custody_context(&spec, head_epoch, epoch_and_cgc_tuples);
 
         // Backfill to epoch 15 (between the two CGC increases)
-        complete_backfill_for_epochs(&custody_context, Epoch::new(20), Epoch::new(15));
+        complete_backfill_for_epochs(&custody_context, Epoch::new(20), Epoch::new(15), final_cgc);
+
+        // Verify epochs 15 - 20 return latest CGC (32)
+        for epoch in 15..=20 {
+            assert_eq!(
+                custody_context.custody_group_count_at_epoch(Epoch::new(epoch), &spec),
+                final_cgc,
+            );
+        }
+
+        // Verify epochs 10-14 still return mid_cgc (16)
+        for epoch in 10..14 {
+            assert_eq!(
+                custody_context.custody_group_count_at_epoch(Epoch::new(epoch), &spec),
+                mid_cgc,
+            );
+        }
+    }
+
+    #[test]
+    fn attempt_backfill_with_invalid_cgc() {
+        let spec = E::default_spec();
+        let initial_cgc = 8u64;
+        let mid_cgc = 16u64;
+        let final_cgc = 32u64;
+
+        // Setup: Node restart after multiple validator registrations causing CGC increases
+        let head_epoch = Epoch::new(20);
+        let epoch_and_cgc_tuples = vec![
+            (Epoch::new(0), initial_cgc),
+            (Epoch::new(10), mid_cgc),
+            (head_epoch, final_cgc),
+        ];
+        let custody_context = setup_custody_context(&spec, head_epoch, epoch_and_cgc_tuples);
+
+        // Backfill to epoch 15 (between the two CGC increases)
+        complete_backfill_for_epochs(&custody_context, Epoch::new(20), Epoch::new(15), final_cgc);
 
         // Verify epochs 15 - 20 return latest CGC (32)
         for epoch in 15..=20 {
@@ -1416,6 +1467,22 @@ mod tests {
             );
         }
 
+        // Attempt backfill with an incorrect cgc value
+        complete_backfill_for_epochs(
+            &custody_context,
+            Epoch::new(20),
+            Epoch::new(15),
+            initial_cgc,
+        );
+
+        // Verify epochs 15 - 20 still return latest CGC (32)
+        for epoch in 15..=20 {
+            assert_eq!(
+                custody_context.custody_group_count_at_epoch(Epoch::new(epoch), &spec),
+                final_cgc,
+            );
+        }
+
         // Verify epochs 10-14 still return mid_cgc (16)
         for epoch in 10..14 {
             assert_eq!(
```

### beacon_node/beacon_chain/src/historical_data_columns.rs
```diff
@@ -54,6 +54,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         &self,
         epoch: Epoch,
         historical_data_column_sidecar_list: DataColumnSidecarList<T::EthSpec>,
+        expected_cgc: u64,
     ) -> Result<usize, HistoricalDataColumnError> {
         let mut total_imported = 0;
         let mut ops = vec![];
@@ -136,7 +137,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
 
         self.data_availability_checker
             .custody_context()
-            .update_and_backfill_custody_count_at_epoch(epoch);
+            .update_and_backfill_custody_count_at_epoch(epoch, expected_cgc);
 
         self.safely_backfill_data_column_custody_info(epoch)
             .map_err(|e| HistoricalDataColumnError::BeaconChainError(Box::new(e)))?;
```

### beacon_node/beacon_chain/tests/store_tests.rs
```diff
@@ -3182,13 +3182,16 @@ async fn weak_subjectivity_sync_test(
     assert_eq!(store.get_anchor_info().state_upper_limit, Slot::new(0));
 }
 
+// This test prunes data columns from epoch 0 and then tries to re-import them via
+// the same code paths that custody backfill sync imports data columns
 #[tokio::test]
 async fn test_import_historical_data_columns_batch() {
     let spec = ForkName::Fulu.make_genesis_spec(E::default_spec());
     let db_path = tempdir().unwrap();
     let store = get_store_generic(&db_path, StoreConfig::default(), spec);
     let start_slot = Epoch::new(0).start_slot(E::slots_per_epoch()) + 1;
     let end_slot = Epoch::new(0).end_slot(E::slots_per_epoch());
+    let cgc = 128;
 
     let harness = get_harness_import_all_data_columns(store.clone(), LOW_VALIDATOR_COUNT);
 
@@ -3208,6 +3211,7 @@ async fn test_import_historical_data_columns_batch() {
 
     let mut data_columns_list = vec![];
 
+    // Get all data columns for epoch 0
     for block in block_root_iter {
         let (block_root, _) = block.unwrap();
         let data_columns = harness.chain.store.get_data_columns(&block_root).unwrap();
@@ -3227,6 +3231,7 @@ async fn test_import_historical_data_columns_batch() {
 
     harness.advance_slot();
 
+    // Prune data columns
     harness
         .chain
         .store
@@ -3238,21 +3243,25 @@ async fn test_import_historical_data_columns_batch() {
         .forwards_iter_block_roots_until(start_slot, end_slot)
         .unwrap();
 
+    // Assert that data columns no longer exist for epoch 0
     for block in block_root_iter {
         let (block_root, _) = block.unwrap();
         let data_columns = harness.chain.store.get_data_columns(&block_root).unwrap();
         assert!(data_columns.is_none())
     }
 
+    // Re-import deleted data columns
     harness
         .chain
-        .import_historical_data_column_batch(Epoch::new(0), data_columns_list)
+        .import_historical_data_column_batch(Epoch::new(0), data_columns_list, cgc)
         .unwrap();
+
     let block_root_iter = harness
         .chain
         .forwards_iter_block_roots_until(start_slot, end_slot)
         .unwrap();
 
+    // Assert that data columns now exist for epoch 0
     for block in block_root_iter {
         let (block_root, _) = block.unwrap();
         let data_columns = harness.chain.store.get_data_columns(&block_root).unwrap();
@@ -3261,13 +3270,15 @@ async fn test_import_historical_data_columns_batch() {
 }
 
 // This should verify that a data column sidecar containing mismatched block roots should fail to be imported.
+// This also covers any test cases related to data columns with incorrect/invalid/mismatched block roots.
 #[tokio::test]
 async fn test_import_historical_data_columns_batch_mismatched_block_root() {
     let spec = ForkName::Fulu.make_genesis_spec(E::default_spec());
     let db_path = tempdir().unwrap();
     let store = get_store_generic(&db_path, StoreConfig::default(), spec);
     let start_slot = Slot::new(1);
     let end_slot = Slot::new(E::slots_per_epoch() * 2 - 1);
+    let cgc = 128;
 
     let harness = get_harness_import_all_data_columns(store.clone(), LOW_VALIDATOR_COUNT);
 
@@ -3287,6 +3298,8 @@ async fn test_import_historical_data_columns_batch_mismatched_block_root() {
 
     let mut data_columns_list = vec![];
 
+    // Get all data columns from start_slot to end_slot
+    // and mutate the data columns with an invalid block root
     for block in block_root_iter {
         let (block_root, _) = block.unwrap();
         let data_columns = harness.chain.store.get_data_columns(&block_root).unwrap();
@@ -3312,6 +3325,7 @@ async fn test_import_historical_data_columns_batch_mismatched_block_root() {
 
     harness.advance_slot();
 
+    // Prune blobs
     harness
         .chain
         .store
@@ -3323,17 +3337,20 @@ async fn test_import_historical_data_columns_batch_mismatched_block_root() {
         .forwards_iter_block_roots_until(start_slot, end_slot)
         .unwrap();
 
+    // Assert there are no columns between start_slot and end_slot
     for block in block_root_iter {
         let (block_root, _) = block.unwrap();
         let data_columns = harness.chain.store.get_data_columns(&block_root).unwrap();
         assert!(data_columns.is_none())
     }
 
+    // Attempt to import data columns with invalid block roots and expect a failure
     let error = harness
         .chain
         .import_historical_data_column_batch(
             start_slot.epoch(E::slots_per_epoch()),
             data_columns_list,
+            cgc,
         )
         .unwrap_err();
 
@@ -3343,84 +3360,6 @@ async fn test_import_historical_data_columns_batch_mismatched_block_root() {
     ));
 }
 
-// This should verify that a data column sidecar associated to a block root that doesn't exist in the store cannot
-// be imported.
-#[tokio::test]
-async fn test_import_historical_data_columns_batch_no_block_found() {
-    let spec = ForkName::Fulu.make_genesis_spec(E::default_spec());
-    let db_path = tempdir().unwrap();
-    let store = get_store_generic(&db_path, StoreConfig::default(), spec);
-    let start_slot = Slot::new(1);
-    let end_slot = Slot::new(E::slots_per_epoch() * 2 - 1);
-
-    let harness = get_harness_import_all_data_columns(store.clone(), LOW_VALIDATOR_COUNT);
-
-    harness
-        .extend_chain(
-            (E::slots_per_epoch() * 2) as usize,
-            BlockStrategy::OnCanonicalHead,
-            AttestationStrategy::AllValidators,
-        )
-        .await;
-    harness.advance_slot();
-
-    let block_root_iter = harness
-        .chain
-        .forwards_iter_block_roots_until(start_slot, end_slot)
-        .unwrap();
-
-    let mut data_columns_list = vec![];
-
-    for block in block_root_iter {
-        let (block_root, _) = block.unwrap();
-        let data_columns = harness.chain.store.get_data_columns(&block_root).unwrap();
-        assert!(data_columns.is_some());
-
-        for data_column in data_columns.unwrap() {
-            let mut data_column = (*data_column).clone();
-            data_column.signed_block_header.message.body_root = Hash256::ZERO;
-            data_columns_list.push(Arc::new(data_column));
-        }
-    }
-
-    harness
-        .extend_chain(
-            (E::slots_per_epoch() * 4) as usize,
-            BlockStrategy::OnCanonicalHead,
-            AttestationStrategy::AllValidators,
-        )
-        .await;
-
-    harness.advance_slot();
-
-    harness
-        .chain
-        .store
-        .try_prune_blobs(true, Epoch::new(2))
-        .unwrap();
-
-    let block_root_iter = harness
-        .chain
-        .forwards_iter_block_roots_until(start_slot, end_slot)
-        .unwrap();
-
-    for block in block_root_iter {
-        let (block_root, _) = block.unwrap();
-        let data_columns = harness.chain.store.get_data_columns(&block_root).unwrap();
-        assert!(data_columns.is_none())
-    }
-
-    let error = harness
-        .chain
-        .import_historical_data_column_batch(Epoch::new(0), data_columns_list)
-        .unwrap_err();
-
-    assert!(matches!(
-        error,
-        HistoricalDataColumnError::NoBlockFound { .. }
-    ));
-}
-
 /// Test that blocks and attestations that refer to states around an unaligned split state are
 /// processed correctly.
 #[tokio::test]
```

### beacon_node/network/src/network_beacon_processor/mod.rs
```diff
@@ -497,9 +497,11 @@ impl<T: BeaconChainTypes> NetworkBeaconProcessor<T> {
         self: &Arc<Self>,
         batch_id: CustodyBackfillBatchId,
         data_columns: DataColumnSidecarList<T::EthSpec>,
+        expected_cgc: u64,
     ) -> Result<(), Error<T::EthSpec>> {
         let processor = self.clone();
-        let process_fn = move || processor.process_historic_data_columns(batch_id, data_columns);
+        let process_fn =
+            move || processor.process_historic_data_columns(batch_id, data_columns, expected_cgc);
 
         let work = Work::ChainSegmentBackfill(Box::new(process_fn));
 
```

### beacon_node/network/src/network_beacon_processor/sync_methods.rs
```diff
@@ -426,6 +426,7 @@ impl<T: BeaconChainTypes> NetworkBeaconProcessor<T> {
         &self,
         batch_id: CustodyBackfillBatchId,
         downloaded_columns: DataColumnSidecarList<T::EthSpec>,
+        expected_cgc: u64,
     ) {
         let _guard = debug_span!(
             SPAN_CUSTODY_BACKFILL_SYNC_IMPORT_COLUMNS,
@@ -435,10 +436,11 @@ impl<T: BeaconChainTypes> NetworkBeaconProcessor<T> {
         .entered();
 
         let sent_columns = downloaded_columns.len();
-        let result = match self
-            .chain
-            .import_historical_data_column_batch(batch_id.epoch, downloaded_columns)
-        {
+        let result = match self.chain.import_historical_data_column_batch(
+            batch_id.epoch,
+            downloaded_columns,
+            expected_cgc,
+        ) {
             Ok(imported_columns) => {
                 metrics::inc_counter_by(
                     &metrics::BEACON_PROCESSOR_CUSTODY_BACKFILL_COLUMN_IMPORT_SUCCESS_TOTAL,
```

### beacon_node/network/src/sync/custody_backfill_sync/mod.rs
```diff
@@ -504,6 +504,7 @@ impl<T: BeaconChainTypes> CustodyBackFillSync<T> {
                 run_id: self.run_id,
             },
             data_columns,
+            self.cgc,
         ) {
             crit!(
                 msg = "process_batch",
```
