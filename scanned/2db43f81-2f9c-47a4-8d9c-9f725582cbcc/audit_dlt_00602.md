# [?] Fix data availability checker race condition causing partial data columns to be served over RPC (#7961)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-09-02
Source: https://github.com/sigp/lighthouse/commit/eef02afc9326c5e7f1855a995debdbcc481f5c14
Type: security-commit

## Details
Fix data availability checker race condition causing partial data columns to be served over RPC (#7961)

Partially resolves #6439, an simpler alternative to #7931.

Race condition occurs when RPC data columns arrives after a block has been imported and removed from the DA checker:
1. Block becomes available via gossip
2. RPC columns arrive and pass fork choice check (block hasn't been imported)
3. Block import completes (removing block from DA checker)
4. RPC data columns finish verification and get imported into DA checker

This causes two issues:
1. **Partial data serving**: Already imported components get re-inserted, potentially causing LH to serve incomplete data
2. **State cache misses**: Leads to state reconstruction, holding the availability cache write lock longer and increasing race likelihood

### Proposed Changes

1. Never manually remove pending components from DA checker. Components are only removed via LRU eviction as finality advances. This makes sure we don't run into the issue described above.
2. Use `get` instead of `pop` when recovering the executed block, this prevents cache misses in race condition. This should reduce the likelihood of the race condition
3. Refactor DA checker to drop write lock as soon as components are added. This should also reduce the likelihood of the race condition

**Trade-offs:**

This solution eliminates a few nasty race conditions while allowing simplicity, with the cost of allowing block re-import (already existing).

The increase in memory in DA checker can be partially offset by a reduction in block cache size if this really comes an issue (as we now serve recent blocks from DA checker).

## Patch
### beacon_node/beacon_chain/src/beacon_chain.rs
```diff
@@ -3815,19 +3815,6 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
             .await??
         };
 
-        // Remove block components from da_checker AFTER completing block import. Then we can assert
-        // the following invariant:
-        // > A valid unfinalized block is either in fork-choice or da_checker.
-        //
-        // If we remove the block when it becomes available, there's some time window during
-        // `import_block` where the block is nowhere. Consumers of the da_checker can handle the
-        // extend time a block may exist in the da_checker.
-        //
-        // If `import_block` errors (only errors with internal errors), the pending components will
-        // be pruned on data_availability_checker maintenance as finality advances.
-        self.data_availability_checker
-            .remove_pending_components(block_root);
-
         Ok(AvailabilityProcessingStatus::Imported(block_root))
     }
 
```

### beacon_node/beacon_chain/src/data_availability_checker.rs
```diff
@@ -38,19 +38,18 @@ use crate::observed_data_sidecars::ObservationStrategy;
 pub use error::{Error as AvailabilityCheckError, ErrorCategory as AvailabilityCheckErrorCategory};
 use types::non_zero_usize::new_non_zero_usize;
 
-/// The LRU Cache stores `PendingComponents`, which can store up to `MAX_BLOBS_PER_BLOCK` blobs each.
+/// The LRU Cache stores `PendingComponents`, which store block and its associated blob data:
 ///
 /// * Deneb blobs are 128 kb each and are stored in the form of `BlobSidecar`.
 /// * From Fulu (PeerDAS), blobs are erasure-coded and are 256 kb each, stored in the form of 128 `DataColumnSidecar`s.
 ///
 /// With `MAX_BLOBS_PER_BLOCK` = 48 (expected in the next year), the maximum size of data columns
-/// in `PendingComponents` is ~12.29 MB. Setting this to 64 means the maximum size of the cache is
-/// approximately 0.8 GB.
+/// in `PendingComponents` is ~12.29 MB. Setting this to 32 means the maximum size of the cache is
+/// approximately 0.4 GB.
 ///
-/// Under normal conditions, the cache should only store the current pending block, but could
-///  occasionally spike to 2-4 for various reasons e.g. components arriving late, but would very
-/// rarely go above this, unless there are many concurrent forks.
-pub const OVERFLOW_LRU_CAPACITY: NonZeroUsize = new_non_zero_usize(64);
+/// `PendingComponents` are now never removed from the cache manually are only removed via LRU
+/// eviction to prevent race conditions (#7961), so we expect this cache to be full all the time.
+pub const OVERFLOW_LRU_CAPACITY: NonZeroUsize = new_non_zero_usize(32);
 pub const STATE_LRU_CAPACITY_NON_ZERO: NonZeroUsize = new_non_zero_usize(32);
 pub const STATE_LRU_CAPACITY: usize = STATE_LRU_CAPACITY_NON_ZERO.get();
 
@@ -346,11 +345,6 @@ impl<T: BeaconChainTypes> DataAvailabilityChecker<T> {
             .put_pending_executed_block(executed_block)
     }
 
-    pub fn remove_pending_components(&self, block_root: Hash256) {
-        self.availability_cache
-            .remove_pending_components(block_root)
-    }
-
     /// Verifies kzg commitments for an RpcBlock, returns a `MaybeAvailableBlock` that may
     /// include the fully available block.
     ///
@@ -589,8 +583,8 @@ impl<T: BeaconChainTypes> DataAvailabilityChecker<T> {
 
         // Check indices from cache again to make sure we don't publish components we've already received.
         let Some(existing_column_indices) = self.cached_data_column_indexes(block_root) else {
-            return Ok(DataColumnReconstructionResult::RecoveredColumnsNotImported(
-                "block already imported",
+            return Err(AvailabilityCheckError::Unexpected(
+                "block no longer exists in the data availability checker".to_string(),
             ));
         };
 
```

### beacon_node/beacon_chain/src/data_availability_checker/overflow_lru_cache.rs
```diff
@@ -11,7 +11,7 @@ use crate::data_availability_checker::{Availability, AvailabilityCheckError};
 use crate::data_column_verification::KzgVerifiedCustodyDataColumn;
 use lighthouse_tracing::SPAN_PENDING_COMPONENTS;
 use lru::LruCache;
-use parking_lot::RwLock;
+use parking_lot::{MappedRwLockReadGuard, RwLock, RwLockReadGuard, RwLockWriteGuard};
 use std::cmp::Ordering;
 use std::num::NonZeroUsize;
 use std::sync::Arc;
@@ -89,18 +89,14 @@ impl<E: EthSpec> PendingComponents<E> {
 
     /// Inserts a block into the cache.
     pub fn insert_block(&mut self, block: DietAvailabilityPendingExecutedBlock<E>) {
-        let _guard = self.span.clone().entered();
-        debug!("Block added to pending components");
         *self.get_cached_block_mut() = Some(block)
     }
 
     /// Inserts a blob at a specific index in the cache.
     ///
     /// Existing blob at the index will be replaced.
     pub fn insert_blob_at_index(&mut self, blob_index: usize, blob: KzgVerifiedBlob<E>) {
-        let _guard = self.span.clone().entered();
         if let Some(b) = self.get_cached_blobs_mut().get_mut(blob_index) {
-            debug!(blob_index, "Blob added to pending components");
             *b = Some(blob);
         }
     }
@@ -140,13 +136,8 @@ impl<E: EthSpec> PendingComponents<E> {
         &mut self,
         kzg_verified_data_columns: I,
     ) -> Result<(), AvailabilityCheckError> {
-        let _guard = self.span.clone().entered();
         for data_column in kzg_verified_data_columns {
             if self.get_cached_data_column(data_column.index()).is_none() {
-                debug!(
-                    column_index = data_column.index(),
-                    "Data column added to pending components"
-                );
                 self.verified_data_columns.push(data_column);
             }
         }
@@ -169,9 +160,9 @@ impl<E: EthSpec> PendingComponents<E> {
     /// WARNING: This function can potentially take a lot of time if the state needs to be
     /// reconstructed from disk. Ensure you are not holding any write locks while calling this.
     pub fn make_available<R>(
-        &mut self,
+        &self,
         spec: &Arc<ChainSpec>,
-        num_expected_columns: usize,
+        num_expected_columns_opt: Option<usize>,
         recover: R,
     ) -> Result<Option<AvailableExecutedBlock<E>>, AvailabilityCheckError>
     where
@@ -188,7 +179,7 @@ impl<E: EthSpec> PendingComponents<E> {
         let num_expected_blobs = block.num_blobs_expected();
         let blob_data = if num_expected_blobs == 0 {
             Some(AvailableBlockData::NoData)
-        } else if spec.is_peer_das_enabled_for_epoch(block.epoch()) {
+        } else if let Some(num_expected_columns) = num_expected_columns_opt {
             let num_received_columns = self.verified_data_columns.len();
             match num_received_columns.cmp(&num_expected_columns) {
                 Ordering::Greater => {
@@ -325,21 +316,14 @@ impl<E: EthSpec> PendingComponents<E> {
         None
     }
 
-    pub fn status_str(
-        &self,
-        block_epoch: Epoch,
-        num_expected_columns: Option<usize>,
-        spec: &ChainSpec,
-    ) -> String {
+    pub fn status_str(&self, num_expected_columns_opt: Option<usize>) -> String {
         let block_count = if self.executed_block.is_some() { 1 } else { 0 };
-        if spec.is_peer_das_enabled_for_epoch(block_epoch) {
+        if let Some(num_expected_columns) = num_expected_columns_opt {
             format!(
                 "block {} data_columns {}/{}",
                 block_count,
                 self.verified_data_columns.len(),
                 num_expected_columns
-                    .map(|c| c.to_string())
-                    .unwrap_or("?".into())
             )
         } else {
             let num_expected_blobs = if let Some(block) = self.get_cached_block() {
@@ -475,41 +459,21 @@ impl<T: BeaconChainTypes> DataAvailabilityCheckerInner<T> {
                 *blob_opt = Some(blob);
             }
         }
+        let pending_components =
+            self.update_or_insert_pending_components(block_root, epoch, |pending_components| {
+                pending_components.merge_blobs(fixed_blobs);
+                Ok(())
+            })?;
+
+        pending_components.span.in_scope(|| {
+            debug!(
+                component = "blobs",
+                status = pending_components.status_str(None),
+                "Component added to data availability checker"
+            );
+        });
 
-        let mut write_lock = self.critical.write();
-
-        // Grab existing entry or create a new entry.
-        let mut pending_components = write_lock
-            .pop_entry(&block_root)
-            .map(|(_, v)| v)
-            .unwrap_or_else(|| {
-                PendingComponents::empty(block_root, self.spec.max_blobs_per_block(epoch) as usize)
-            });
-
-        // Merge in the blobs.
-        pending_components.merge_blobs(fixed_blobs);
-
-        debug!(
-            component = "blobs",
-            ?block_root,
-            status = pending_components.status_str(epoch, None, &self.spec),
-            "Component added to data availability checker"
-        );
-
-        if let Some(available_block) = pending_components.make_available(
-            &self.spec,
-            self.custody_context
-                .num_of_data_columns_to_sample(epoch, &self.spec),
-            |block, span| self.state_cache.recover_pending_executed_block(block, span),
-        )? {
-            // We keep the pending components in the availability cache during block import (#5845).
-            write_lock.put(block_root, pending_components);
-            drop(write_lock);
-            Ok(Availability::Available(Box::new(available_block)))
-        } else {
-            write_lock.put(block_root, pending_components);
-            Ok(Availability::MissingComponents(block_root))
-        }
+        self.check_availability_and_cache_components(block_root, pending_components, None)
     }
 
     #[allow(clippy::type_complexity)]
@@ -532,44 +496,91 @@ impl<T: BeaconChainTypes> DataAvailabilityCheckerInner<T> {
             return Ok(Availability::MissingComponents(block_root));
         };
 
-        let mut write_lock = self.critical.write();
-
-        // Grab existing entry or create a new entry.
-        let mut pending_components = write_lock
-            .pop_entry(&block_root)
-            .map(|(_, v)| v)
-            .unwrap_or_else(|| {
-                PendingComponents::empty(block_root, self.spec.max_blobs_per_block(epoch) as usize)
-            });
-
-        // Merge in the data columns.
-        pending_components.merge_data_columns(kzg_verified_data_columns)?;
+        let pending_components =
+            self.update_or_insert_pending_components(block_root, epoch, |pending_components| {
+                pending_components.merge_data_columns(kzg_verified_data_columns)
+            })?;
 
         let num_expected_columns = self
             .custody_context
             .num_of_data_columns_to_sample(epoch, &self.spec);
-        debug!(
-            component = "data_columns",
-            ?block_root,
-            status = pending_components.status_str(epoch, Some(num_expected_columns), &self.spec),
-            "Component added to data availability checker"
-        );
 
-        if let Some(available_block) =
-            pending_components.make_available(&self.spec, num_expected_columns, |block, span| {
-                self.state_cache.recover_pending_executed_block(block, span)
-            })?
-        {
-            // We keep the pending components in the availability cache during block import (#5845).
-            write_lock.put(block_root, pending_components);
-            drop(write_lock);
+        pending_components.span.in_scope(|| {
+            debug!(
+                component = "data_columns",
+                status = pending_components.status_str(Some(num_expected_columns)),
+                "Component added to data availability checker"
+            );
+        });
+
+        self.check_availability_and_cache_components(
+            block_root,
+            pending_components,
+            Some(num_expected_columns),
+        )
+    }
+
+    fn check_availability_and_cache_components(
+        &self,
+        block_root: Hash256,
+        pending_components: MappedRwLockReadGuard<'_, PendingComponents<T::EthSpec>>,
+        num_expected_columns_opt: Option<usize>,
+    ) -> Result<Availability<T::EthSpec>, AvailabilityCheckError> {
+        if let Some(available_block) = pending_components.make_available(
+            &self.spec,
+            num_expected_columns_opt,
+            |block, span| self.state_cache.recover_pending_executed_block(block, span),
+        )? {
+            // Explicitly drop read lock before acquiring write lock
+            drop(pending_components);
+            if let Some(components) = self.critical.write().get_mut(&block_root) {
+                // Clean up span now that block is available
+                components.span = Span::none();
+            }
+
+            // We never remove the pending components manually to avoid race conditions.
+            // This ensures components remain available during and right after block import,
+            // preventing a race condition where a component was removed after the block was
+            // imported, but re-inserted immediately, causing partial pending components to be
+            // stored and served to peers.
+            // Components are only removed via LRU eviction as finality advances.
             Ok(Availability::Available(Box::new(available_block)))
         } else {
-            write_lock.put(block_root, pending_components);
             Ok(Availability::MissingComponents(block_root))
         }
     }
 
+    /// Updates or inserts a new `PendingComponents` if it doesn't exist, and then apply the
+    /// `update_fn` while holding the write lock.
+    ///
+    /// Once the update is complete, the write lock is downgraded and a read guard with a
+    /// reference of the updated `PendingComponents` is returned.
+    fn update_or_insert_pending_components<F>(
+        &self,
+        block_root: Hash256,
+        epoch: Epoch,
+        update_fn: F,
+    ) -> Result<MappedRwLockReadGuard<'_, PendingComponents<T::EthSpec>>, AvailabilityCheckError>
+    where
+        F: FnOnce(&mut PendingComponents<T::EthSpec>) -> Result<(), AvailabilityCheckError>,
+    {
+        let mut write_lock = self.critical.write();
+
+        {
+            let pending_components = write_lock.get_or_insert_mut(block_root, || {
+                PendingComponents::empty(block_root, self.spec.max_blobs_per_block(epoch) as usize)
+            });
+            update_fn(pending_components)?
+        }
+
+        RwLockReadGuard::try_map(RwLockWriteGuard::downgrade(write_lock), |cache| {
+            cache.peek(&block_root)
+        })
+        .map_err(|_| {
+            AvailabilityCheckError::Unexpected("pending components should exist".to_string())
+        })
+    }
+
     /// Check whether data column reconstruction should be attempted.
     ///
     /// Potentially trigger reconstruction if:
@@ -623,7 +634,6 @@ impl<T: BeaconChainTypes> DataAvailabilityCheckerInner<T> {
         &self,
         executed_block: AvailabilityPendingExecutedBlock<T::EthSpec>,
     ) -> Result<Availability<T::EthSpec>, AvailabilityCheckError> {
-        let mut write_lock = self.critical.write();
         let epoch = executed_block.as_block().epoch();
         let block_root = executed_block.import_data.block_root;
 
@@ -632,45 +642,32 @@ impl<T: BeaconChainTypes> DataAvailabilityCheckerInner<T> {
             .state_cache
             .register_pending_executed_block(executed_block);
 
-        // Grab existing entry or create a new entry.
-        let mut pending_components = write_lock
-            .pop_entry(&block_root)
-            .map(|(_, v)| v)
-            .unwrap_or_else(|| {
-                PendingComponents::empty(block_root, self.spec.max_blobs_per_block(epoch) as usize)
-            });
-
-        // Merge in the block.
-        pending_components.merge_block(diet_executed_block);
+        let pending_components =
+            self.update_or_insert_pending_components(block_root, epoch, |pending_components| {
+                pending_components.merge_block(diet_executed_block);
+                Ok(())
+            })?;
+
+        let num_expected_columns_opt = if self.spec.is_peer_das_enabled_for_epoch(epoch) {
+            let num_of_column_samples = self
+                .custody_context
+                .num_of_data_columns_to_sample(epoch, &self.spec);
+            Some(num_of_column_samples)
+        } else {
+            None
+        };
 
-        let num_expected_columns = self
-            .custody_context
-            .num_of_data_columns_to_sample(epoch, &self.spec);
         debug!(
             component = "block",
-            ?block_root,
-            status = pending_components.status_str(epoch, Some(num_expected_columns), &self.spec),
+            status = pending_components.status_str(num_expected_columns_opt),
             "Component added to data availability checker"
         );
 
-        // Check if we have all components and entire set is consistent.
-        if let Some(available_block) =
-            pending_components.make_available(&self.spec, num_expected_columns, |block, span| {
-                self.state_cache.recover_pending_executed_block(block, span)
-            })?
-        {
-            // We keep the pending components in the availability cache during block import (#5845).
-            write_lock.put(block_root, pending_components);
-            drop(write_lock);
-            Ok(Availability::Available(Box::new(available_block)))
-        } else {
-            write_lock.put(block_root, pending_components);
-            Ok(Availability::MissingComponents(block_root))
-        }
-    }
-
-    pub fn remove_pending_components(&self, block_root: Hash256) {
-        self.critical.write().pop_entry(&block_root);
+        self.check_availability_and_cache_components(
+            block_root,
+            pending_components,
+            num_expected_columns_opt,
+        )
     }
 
     /// maintain the cache
@@ -958,13 +955,6 @@ mod test {
                 1,
                 "cache should still have block as it hasn't been imported yet"
             );
-            // remove the blob to simulate successful import
-            cache.remove_pending_components(root);
-            assert_eq!(
-                cache.critical.read().len(),
-                0,
-                "cache should be empty now that block has been imported"
-            );
         } else {
             assert!(
                 matches!(availability, Availability::MissingComponents(_)),
@@ -994,12 +984,6 @@ mod test {
                 assert_eq!(cache.critical.read().len(), 1);
             }
         }
-        // remove the blob to simulate successful import
-        cache.remove_pending_components(root);
-        assert!(
-            cache.critical.read().is_empty(),
-            "cache should be empty now that all components available"
-        );
 
         let (pending_block, blobs) = availability_pending_block(&harness).await;
         let blobs_expected = pending_block.num_blobs_expected();
@@ -1019,7 +1003,11 @@ mod test {
                 matches!(availability, Availability::MissingComponents(_)),
                 "should be pending block"
             );
-            assert_eq!(cache.critical.read().len(), 1);
+            assert_eq!(
+                cache.critical.read().len(),
+                2,
+                "cache should have two blocks now"
+            );
         }
         let availability = cache
             .put_pending_executed_block(pending_block)
@@ -1030,14 +1018,8 @@ mod test {
             availability
         );
         assert!(
-            cache.critical.read().len() == 1,
-            "cache should still have available block until import"
-        );
-        // remove the blob to simulate successful import
-        cache.remove_pending_components(root);
-        assert!(
-            cache.critical.read().is_empty(),
-            "cache should be empty now that all components available"
+            cache.critical.read().len() == 2,
+            "cache should still have available block"
         );
     }
 
@@ -1159,14 +1141,6 @@ mod test {
             states.last(),
             "recovered state should be the same as the original"
         );
-        // the state should no longer be in the cache
-        assert!(
-            state_cache
-                .read()
-                .peek(&last_block.as_block().state_root())
-                .is_none(),
-            "last block state should no longer be in cache"
-        );
     }
 }
 
```

### beacon_node/beacon_chain/src/data_availability_checker/state_lru_cache.rs
```diff
@@ -113,8 +113,9 @@ impl<T: BeaconChainTypes> StateLRUCache<T> {
         diet_executed_block: DietAvailabilityPendingExecutedBlock<T::EthSpec>,
         _span: &Span,
     ) -> Result<AvailabilityPendingExecutedBlock<T::EthSpec>, AvailabilityCheckError> {
-        let state = if let Some(state) = self.states.write().pop(&diet_executed_block.state_root) {
-            state
+        // Keep the state in the cache to prevent reconstruction in race conditions
+        let state = if let Some(state) = self.states.write().get(&diet_executed_block.state_root) {
+            state.clone()
         } else {
             self.reconstruct_state(&diet_executed_block)?
         };
```
