# [?] Fix data columns not persisting for PeerDAS due to a `getBlobs` race condition (#6756)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-01-15
Source: https://github.com/sigp/lighthouse/commit/dd7591f7123dfe072631c0deb0abc1b78cc82733
Type: security-commit

## Details
Fix data columns not persisting for PeerDAS due to a `getBlobs` race condition (#6756)

* Fix data columns not persisting for PeerDAS due to a `getBlobs` race condition.

* Refactor blobs and columns logic in `chain.import_block` for clarity. Add more docs on `data_column_recv`.

* Add more code comments for clarity.

* Merge remote-tracking branch 'origin/unstable' into fix-column-race

# Conflicts:
#	beacon_node/beacon_chain/src/block_verification_types.rs
#	beacon_node/beacon_chain/src/data_availability_checker/overflow_lru_cache.rs

* Fix lint.

## Patch
### beacon_node/beacon_chain/src/beacon_chain.rs
```diff
@@ -121,7 +121,7 @@ use store::{
     KeyValueStoreOp, StoreItem, StoreOp,
 };
 use task_executor::{ShutdownReason, TaskExecutor};
-use tokio::sync::mpsc::Receiver;
+use tokio::sync::oneshot;
 use tokio_stream::Stream;
 use tree_hash::TreeHash;
 use types::blob_sidecar::FixedBlobSidecarList;
@@ -3088,7 +3088,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         slot: Slot,
         block_root: Hash256,
         blobs: FixedBlobSidecarList<T::EthSpec>,
-        data_column_recv: Option<Receiver<DataColumnSidecarList<T::EthSpec>>>,
+        data_column_recv: Option<oneshot::Receiver<DataColumnSidecarList<T::EthSpec>>>,
     ) -> Result<AvailabilityProcessingStatus, BlockError> {
         // If this block has already been imported to forkchoice it must have been available, so
         // we don't need to process its blobs again.
@@ -3216,7 +3216,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
                 };
 
                 let r = self
-                    .process_availability(slot, availability, None, || Ok(()))
+                    .process_availability(slot, availability, || Ok(()))
                     .await;
                 self.remove_notified(&block_root, r)
                     .map(|availability_processing_status| {
@@ -3344,7 +3344,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
 
             match executed_block {
                 ExecutedBlock::Available(block) => {
-                    self.import_available_block(Box::new(block), None).await
+                    self.import_available_block(Box::new(block)).await
                 }
                 ExecutedBlock::AvailabilityPending(block) => {
                     self.check_block_availability_and_import(block).await
@@ -3476,7 +3476,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         let availability = self
             .data_availability_checker
             .put_pending_executed_block(block)?;
-        self.process_availability(slot, availability, None, || Ok(()))
+        self.process_availability(slot, availability, || Ok(()))
             .await
     }
 
@@ -3492,7 +3492,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         }
         let availability = self.data_availability_checker.put_gossip_blob(blob)?;
 
-        self.process_availability(slot, availability, None, || Ok(()))
+        self.process_availability(slot, availability, || Ok(()))
             .await
     }
 
@@ -3515,7 +3515,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
             .data_availability_checker
             .put_gossip_data_columns(block_root, data_columns)?;
 
-        self.process_availability(slot, availability, None, publish_fn)
+        self.process_availability(slot, availability, publish_fn)
             .await
     }
 
@@ -3559,7 +3559,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
             .data_availability_checker
             .put_rpc_blobs(block_root, blobs)?;
 
-        self.process_availability(slot, availability, None, || Ok(()))
+        self.process_availability(slot, availability, || Ok(()))
             .await
     }
 
@@ -3568,14 +3568,14 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         slot: Slot,
         block_root: Hash256,
         blobs: FixedBlobSidecarList<T::EthSpec>,
-        data_column_recv: Option<Receiver<DataColumnSidecarList<T::EthSpec>>>,
+        data_column_recv: Option<oneshot::Receiver<DataColumnSidecarList<T::EthSpec>>>,
     ) -> Result<AvailabilityProcessingStatus, BlockError> {
         self.check_blobs_for_slashability(block_root, &blobs)?;
-        let availability = self
-            .data_availability_checker
-            .put_engine_blobs(block_root, blobs)?;
+        let availability =
+            self.data_availability_checker
+                .put_engine_blobs(block_root, blobs, data_column_recv)?;
 
-        self.process_availability(slot, availability, data_column_recv, || Ok(()))
+        self.process_availability(slot, availability, || Ok(()))
             .await
     }
 
@@ -3615,7 +3615,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
             .data_availability_checker
             .put_rpc_custody_columns(block_root, custody_columns)?;
 
-        self.process_availability(slot, availability, None, || Ok(()))
+        self.process_availability(slot, availability, || Ok(()))
             .await
     }
 
@@ -3627,14 +3627,13 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         self: &Arc<Self>,
         slot: Slot,
         availability: Availability<T::EthSpec>,
-        recv: Option<Receiver<DataColumnSidecarList<T::EthSpec>>>,
         publish_fn: impl FnOnce() -> Result<(), BlockError>,
     ) -> Result<AvailabilityProcessingStatus, BlockError> {
         match availability {
             Availability::Available(block) => {
                 publish_fn()?;
                 // Block is fully available, import into fork choice
-                self.import_available_block(block, recv).await
+                self.import_available_block(block).await
             }
             Availability::MissingComponents(block_root) => Ok(
                 AvailabilityProcessingStatus::MissingComponents(slot, block_root),
@@ -3645,7 +3644,6 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
     pub async fn import_available_block(
         self: &Arc<Self>,
         block: Box<AvailableExecutedBlock<T::EthSpec>>,
-        data_column_recv: Option<Receiver<DataColumnSidecarList<T::EthSpec>>>,
     ) -> Result<AvailabilityProcessingStatus, BlockError> {
         let AvailableExecutedBlock {
             block,
@@ -3660,6 +3658,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
             parent_eth1_finalization_data,
             confirmed_state_roots,
             consensus_context,
+            data_column_recv,
         } = import_data;
 
         // Record the time at which this block's blobs became available.
@@ -3726,7 +3725,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         parent_block: SignedBlindedBeaconBlock<T::EthSpec>,
         parent_eth1_finalization_data: Eth1FinalizationData,
         mut consensus_context: ConsensusContext<T::EthSpec>,
-        data_column_recv: Option<Receiver<DataColumnSidecarList<T::EthSpec>>>,
+        data_column_recv: Option<oneshot::Receiver<DataColumnSidecarList<T::EthSpec>>>,
     ) -> Result<Hash256, BlockError> {
         // ----------------------------- BLOCK NOT YET ATTESTABLE ----------------------------------
         // Everything in this initial section is on the hot path between processing the block and
@@ -3894,44 +3893,32 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         // end up with blocks in fork choice that are missing from disk.
         // See https://github.com/sigp/lighthouse/issues/2028
         let (_, signed_block, blobs, data_columns) = signed_block.deconstruct();
-        // TODO(das) we currently store all subnet sampled columns. Tracking issue to exclude non
-        // custody columns: https://github.com/sigp/lighthouse/issues/6465
-        let custody_columns_count = self.data_availability_checker.get_sampling_column_count();
-        // if block is made available via blobs, dropped the data columns.
-        let data_columns = data_columns.filter(|columns| columns.len() == custody_columns_count);
-
-        let data_columns = match (data_columns, data_column_recv) {
-            // If the block was made available via custody columns received from gossip / rpc, use them
-            // since we already have them.
-            (Some(columns), _) => Some(columns),
-            // Otherwise, it means blobs were likely available via fetching from EL, in this case we
-            // wait for the data columns to be computed (blocking).
-            (None, Some(mut data_column_recv)) => {
-                let _column_recv_timer =
-                    metrics::start_timer(&metrics::BLOCK_PROCESSING_DATA_COLUMNS_WAIT);
-                // Unable to receive data columns from sender, sender is either dropped or
-                // failed to compute data columns from blobs. We restore fork choice here and
-                // return to avoid inconsistency in database.
-                if let Some(columns) = data_column_recv.blocking_recv() {
-                    Some(columns)
-                } else {
-                    let err_msg = "Did not receive data columns from sender";
-                    error!(
-                        self.log,
-                        "Failed to store data columns into the database";
-                        "msg" => "Restoring fork choice from disk",
-                        "error" => err_msg,
-                    );
-                    return Err(self
-                        .handle_import_block_db_write_error(fork_choice)
-                        .err()
-                        .unwrap_or(BlockError::InternalError(err_msg.to_string())));
-                }
+
+        match self.get_blobs_or_columns_store_op(
+            block_root,
+            signed_block.epoch(),
+            blobs,
+            data_columns,
+            data_column_recv,
+        ) {
+            Ok(Some(blobs_or_columns_store_op)) => {
+                ops.push(blobs_or_columns_store_op);
             }
-            // No data columns present and compute data columns task was not spawned.
-            // Could either be no blobs in the block or before PeerDAS activation.
-            (None, None) => None,
-        };
+            Ok(None) => {}
+            Err(e) => {
+                error!(
+                    self.log,
+                    "Failed to store data columns into the database";
+                    "msg" => "Restoring fork choice from disk",
+                    "error" => &e,
+                    "block_root" => ?block_root
+                );
+                return Err(self
+                    .handle_import_block_db_write_error(fork_choice)
+                    .err()
+                    .unwrap_or(BlockError::InternalError(e)));
+            }
+        }
 
         let block = signed_block.message();
         let db_write_timer = metrics::start_timer(&metrics::BLOCK_PROCESSING_DB_WRITE);
@@ -3943,30 +3930,6 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         ops.push(StoreOp::PutBlock(block_root, signed_block.clone()));
         ops.push(StoreOp::PutState(block.state_root(), &state));
 
-        if let Some(blobs) = blobs {
-            if !blobs.is_empty() {
-                debug!(
-                    self.log, "Writing blobs to store";
-                    "block_root" => %block_root,
-                    "count" => blobs.len(),
-                );
-                ops.push(StoreOp::PutBlobs(block_root, blobs));
-            }
-        }
-
-        if let Some(data_columns) = data_columns {
-            // TODO(das): `available_block includes all sampled columns, but we only need to store
-            // custody columns. To be clarified in spec.
-            if !data_columns.is_empty() {
-                debug!(
-                    self.log, "Writing data_columns to store";
-                    "block_root" => %block_root,
-                    "count" => data_columns.len(),
-                );
-                ops.push(StoreOp::PutDataColumns(block_root, data_columns));
-            }
-        }
-
         let txn_lock = self.store.hot_db.begin_rw_transaction();
 
         if let Err(e) = self.store.do_atomically_with_block_and_blobs_cache(ops) {
@@ -7184,6 +7147,68 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
             reqresp_pre_import_cache_len: self.reqresp_pre_import_cache.read().len(),
         }
     }
+
+    fn get_blobs_or_columns_store_op(
+        &self,
+        block_root: Hash256,
+        block_epoch: Epoch,
+        blobs: Option<BlobSidecarList<T::EthSpec>>,
+        data_columns: Option<DataColumnSidecarList<T::EthSpec>>,
+        data_column_recv: Option<oneshot::Receiver<DataColumnSidecarList<T::EthSpec>>>,
+    ) -> Result<Option<StoreOp<T::EthSpec>>, String> {
+        if self.spec.is_peer_das_enabled_for_epoch(block_epoch) {
+            // TODO(das) we currently store all subnet sampled columns. Tracking issue to exclude non
+            // custody columns: https://github.com/sigp/lighthouse/issues/6465
+            let custody_columns_count = self.data_availability_checker.get_sampling_column_count();
+
+            let custody_columns_available = data_columns
+                .as_ref()
+                .as_ref()
+                .is_some_and(|columns| columns.len() == custody_columns_count);
+
+            let data_columns_to_persist = if custody_columns_available {
+                // If the block was made available via custody columns received from gossip / rpc, use them
+                // since we already have them.
+                data_columns
+            } else if let Some(data_column_recv) = data_column_recv {
+                // Blobs were available from the EL, in this case we wait for the data columns to be computed (blocking).
+                let _column_recv_timer =
+                    metrics::start_timer(&metrics::BLOCK_PROCESSING_DATA_COLUMNS_WAIT);
+                // Unable to receive data columns from sender, sender is either dropped or
+                // failed to compute data columns from blobs. We restore fork choice here and
+                // return to avoid inconsistency in database.
+                let computed_data_columns = data_column_recv
+                    .blocking_recv()
+                    .map_err(|e| format!("Did not receive data columns from sender: {e:?}"))?;
+                Some(computed_data_columns)
+            } else {
+                // No blobs in the block.
+                None
+            };
+
+            if let Some(data_columns) = data_columns_to_persist {
+                if !data_columns.is_empty() {
+                    debug!(
+                        self.log, "Writing data_columns to store";
+                        "block_root" => %block_root,
+                        "count" => data_columns.len(),
+                    );
+                    return Ok(Some(StoreOp::PutDataColumns(block_root, data_columns)));
+                }
+            }
+        } else if let Some(blobs) = blobs {
+            if !blobs.is_empty() {
+                debug!(
+                    self.log, "Writing blobs to store";
+                    "block_root" => %block_root,
+                    "count" => blobs.len(),
+                );
+                return Ok(Some(StoreOp::PutBlobs(block_root, blobs)));
+            }
+        }
+
+        Ok(None)
+    }
 }
 
 impl<T: BeaconChainTypes> Drop for BeaconChain<T> {
```

### beacon_node/beacon_chain/src/block_verification.rs
```diff
@@ -1677,6 +1677,7 @@ impl<T: BeaconChainTypes> ExecutionPendingBlock<T> {
                 parent_eth1_finalization_data,
                 confirmed_state_roots,
                 consensus_context,
+                data_column_recv: None,
             },
             payload_verification_handle,
         })
```

### beacon_node/beacon_chain/src/block_verification_types.rs
```diff
@@ -7,10 +7,11 @@ use derivative::Derivative;
 use state_processing::ConsensusContext;
 use std::fmt::{Debug, Formatter};
 use std::sync::Arc;
+use tokio::sync::oneshot;
 use types::blob_sidecar::BlobIdentifier;
 use types::{
-    BeaconBlockRef, BeaconState, BlindedPayload, BlobSidecarList, ChainSpec, Epoch, EthSpec,
-    Hash256, RuntimeVariableList, SignedBeaconBlock, SignedBeaconBlockHeader, Slot,
+    BeaconBlockRef, BeaconState, BlindedPayload, BlobSidecarList, ChainSpec, DataColumnSidecarList,
+    Epoch, EthSpec, Hash256, RuntimeVariableList, SignedBeaconBlock, SignedBeaconBlockHeader, Slot,
 };
 
 /// A block that has been received over RPC. It has 2 internal variants:
@@ -337,14 +338,21 @@ impl<E: EthSpec> AvailabilityPendingExecutedBlock<E> {
     }
 }
 
-#[derive(Debug, PartialEq)]
+#[derive(Debug, Derivative)]
+#[derivative(PartialEq)]
 pub struct BlockImportData<E: EthSpec> {
     pub block_root: Hash256,
     pub state: BeaconState<E>,
     pub parent_block: SignedBeaconBlock<E, BlindedPayload<E>>,
     pub parent_eth1_finalization_data: Eth1FinalizationData,
     pub confirmed_state_roots: Vec<Hash256>,
     pub consensus_context: ConsensusContext<E>,
+    #[derivative(PartialEq = "ignore")]
+    /// An optional receiver for `DataColumnSidecarList`.
+    ///
+    /// This field is `Some` when data columns are being computed asynchronously.
+    /// The resulting `DataColumnSidecarList` will be sent through this receiver.
+    pub data_column_recv: Option<oneshot::Receiver<DataColumnSidecarList<E>>>,
 }
 
 impl<E: EthSpec> BlockImportData<E> {
@@ -363,6 +371,7 @@ impl<E: EthSpec> BlockImportData<E> {
             },
             confirmed_state_roots: vec![],
             consensus_context: ConsensusContext::new(Slot::new(0)),
+            data_column_recv: None,
         }
     }
 }
```

### beacon_node/beacon_chain/src/data_availability_checker.rs
```diff
@@ -15,6 +15,7 @@ use std::num::NonZeroUsize;
 use std::sync::Arc;
 use std::time::Duration;
 use task_executor::TaskExecutor;
+use tokio::sync::oneshot;
 use types::blob_sidecar::{BlobIdentifier, BlobSidecar, FixedBlobSidecarList};
 use types::{
     BlobSidecarList, ChainSpec, DataColumnIdentifier, DataColumnSidecar, DataColumnSidecarList,
@@ -223,7 +224,7 @@ impl<T: BeaconChainTypes> DataAvailabilityChecker<T> {
         .map_err(AvailabilityCheckError::InvalidBlobs)?;
 
         self.availability_cache
-            .put_kzg_verified_blobs(block_root, verified_blobs, &self.log)
+            .put_kzg_verified_blobs(block_root, verified_blobs, None, &self.log)
     }
 
     /// Put a list of custody columns received via RPC into the availability cache. This performs KZG
@@ -263,6 +264,7 @@ impl<T: BeaconChainTypes> DataAvailabilityChecker<T> {
         &self,
         block_root: Hash256,
         blobs: FixedBlobSidecarList<T::EthSpec>,
+        data_column_recv: Option<oneshot::Receiver<DataColumnSidecarList<T::EthSpec>>>,
     ) -> Result<Availability<T::EthSpec>, AvailabilityCheckError> {
         let seen_timestamp = self
             .slot_clock
@@ -272,8 +274,12 @@ impl<T: BeaconChainTypes> DataAvailabilityChecker<T> {
         let verified_blobs =
             KzgVerifiedBlobList::from_verified(blobs.iter().flatten().cloned(), seen_timestamp);
 
-        self.availability_cache
-            .put_kzg_verified_blobs(block_root, verified_blobs, &self.log)
+        self.availability_cache.put_kzg_verified_blobs(
+            block_root,
+            verified_blobs,
+            data_column_recv,
+            &self.log,
+        )
     }
 
     /// Check if we've cached other blobs for this block. If it completes a set and we also
@@ -288,6 +294,7 @@ impl<T: BeaconChainTypes> DataAvailabilityChecker<T> {
         self.availability_cache.put_kzg_verified_blobs(
             gossip_blob.block_root(),
             vec![gossip_blob.into_inner()],
+            None,
             &self.log,
         )
     }
@@ -803,7 +810,6 @@ impl<E: EthSpec> AvailableBlock<E> {
             block,
             blobs,
             data_columns,
-            blobs_available_timestamp: _,
             ..
         } = self;
         (block_root, block, blobs, data_columns)
```

### beacon_node/beacon_chain/src/data_availability_checker/overflow_lru_cache.rs
```diff
@@ -12,28 +12,46 @@ use parking_lot::RwLock;
 use slog::{debug, Logger};
 use std::num::NonZeroUsize;
 use std::sync::Arc;
+use tokio::sync::oneshot;
 use types::blob_sidecar::BlobIdentifier;
 use types::{
-    BlobSidecar, ChainSpec, ColumnIndex, DataColumnIdentifier, DataColumnSidecar, Epoch, EthSpec,
-    Hash256, RuntimeFixedVector, RuntimeVariableList, SignedBeaconBlock,
+    BlobSidecar, ChainSpec, ColumnIndex, DataColumnIdentifier, DataColumnSidecar,
+    DataColumnSidecarList, Epoch, EthSpec, Hash256, RuntimeFixedVector, RuntimeVariableList,
+    SignedBeaconBlock,
 };
 
 /// This represents the components of a partially available block
 ///
 /// The blobs are all gossip and kzg verified.
 /// The block has completed all verifications except the availability check.
-/// TODO(das): this struct can potentially be reafactored as blobs and data columns are mutually
-/// exclusive and this could simplify `is_importable`.
-#[derive(Clone)]
 pub struct PendingComponents<E: EthSpec> {
     pub block_root: Hash256,
     pub verified_blobs: RuntimeFixedVector<Option<KzgVerifiedBlob<E>>>,
     pub verified_data_columns: Vec<KzgVerifiedCustodyDataColumn<E>>,
     pub executed_block: Option<DietAvailabilityPendingExecutedBlock<E>>,
     pub reconstruction_started: bool,
+    /// Receiver for data columns that are computed asynchronously;
+    ///
+    /// If `data_column_recv` is `Some`, it means data column computation or reconstruction has been
+    /// started. This can happen either via engine blobs fetching or data column reconstruction
+    /// (triggered when >= 50% columns are received via gossip).
+    pub data_column_recv: Option<oneshot::Receiver<DataColumnSidecarList<E>>>,
 }
 
 impl<E: EthSpec> PendingComponents<E> {
+    /// Clones the `PendingComponent` without cloning `data_column_recv`, as `Receiver` is not cloneable.
+    /// This should only be used when the receiver is no longer needed.
+    pub fn clone_without_column_recv(&self) -> Self {
+        PendingComponents {
+            block_root: self.block_root,
+            verified_blobs: self.verified_blobs.clone(),
+            verified_data_columns: self.verified_data_columns.clone(),
+            executed_block: self.executed_block.clone(),
+            reconstruction_started: self.reconstruction_started,
+            data_column_recv: None,
+        }
+    }
+
     /// Returns an immutable reference to the cached block.
     pub fn get_cached_block(&self) -> &Option<DietAvailabilityPendingExecutedBlock<E>> {
         &self.executed_block
@@ -236,6 +254,7 @@ impl<E: EthSpec> PendingComponents<E> {
             verified_data_columns: vec![],
             executed_block: None,
             reconstruction_started: false,
+            data_column_recv: None,
         }
     }
 
@@ -260,6 +279,7 @@ impl<E: EthSpec> PendingComponents<E> {
             verified_blobs,
             verified_data_columns,
             executed_block,
+            data_column_recv,
             ..
         } = self;
 
@@ -302,10 +322,12 @@ impl<E: EthSpec> PendingComponents<E> {
 
         let AvailabilityPendingExecutedBlock {
             block,
-            import_data,
+            mut import_data,
             payload_verification_outcome,
         } = executed_block;
 
+        import_data.data_column_recv = data_column_recv;
+
         let available_block = AvailableBlock {
             block_root,
             block,
@@ -444,10 +466,17 @@ impl<T: BeaconChainTypes> DataAvailabilityCheckerInner<T> {
         f(self.critical.read().peek(block_root))
     }
 
+    /// Puts the KZG verified blobs into the availability cache as pending components.
+    ///
+    /// The `data_column_recv` parameter is an optional `Receiver` for data columns that are
+    /// computed asynchronously. This method remains **used** after PeerDAS activation, because
+    /// blocks can be made available if the EL already has the blobs and returns them via the
+    /// `getBlobsV1` engine method. More details in [fetch_blobs.rs](https://github.com/sigp/lighthouse/blob/44f8add41ea2252769bb967864af95b3c13af8ca/beacon_node/beacon_chain/src/fetch_blobs.rs).
     pub fn put_kzg_verified_blobs<I: IntoIterator<Item = KzgVerifiedBlob<T::EthSpec>>>(
         &self,
         block_root: Hash256,
         kzg_verified_blobs: I,
+        data_column_recv: Option<oneshot::Receiver<DataColumnSidecarList<T::EthSpec>>>,
         log: &Logger,
     ) -> Result<Availability<T::EthSpec>, AvailabilityCheckError> {
         let mut kzg_verified_blobs = kzg_verified_blobs.into_iter().peekable();
@@ -482,9 +511,17 @@ impl<T: BeaconChainTypes> DataAvailabilityCheckerInner<T> {
         // Merge in the blobs.
         pending_components.merge_blobs(fixed_blobs);
 
+        if data_column_recv.is_some() {
+            // If `data_column_recv` is `Some`, it means we have all the blobs from engine, and have
+            // started computing data columns. We store the receiver in `PendingComponents` for
+            // later use when importing the block.
+            pending_components.data_column_recv = data_column_recv;
+        }
+
         if pending_components.is_available(self.sampling_column_count, log) {
-            write_lock.put(block_root, pending_components.clone());
-            // No need to hold the write lock anymore
+            // We keep the pending components in the availability cache during block import (#5845).
+            // `data_column_recv` is returned as part of the available block and is no longer needed here.
+            write_lock.put(block_root, pending_components.clone_without_column_recv());
             drop(write_lock);
             pending_components.make_available(&self.spec, |diet_block| {
                 self.state_cache.recover_pending_executed_block(diet_block)
@@ -527,8 +564,9 @@ impl<T: BeaconChainTypes> DataAvailabilityCheckerInner<T> {
         pending_components.merge_data_columns(kzg_verified_data_columns)?;
 
         if pending_components.is_available(self.sampling_column_count, log) {
-            write_lock.put(block_root, pending_components.clone());
-            // No need to hold the write lock anymore
+            // We keep the pending components in the availability cache during block import (#5845).
+            // `data_column_recv` is returned as part of the available block and is no longer needed here.
+            write_lock.put(block_root, pending_components.clone_without_column_recv());
             drop(write_lock);
             pending_components.make_available(&self.spec, |diet_block| {
                 self.state_cache.recover_pending_executed_block(diet_block)
@@ -577,7 +615,7 @@ impl<T: BeaconChainTypes> DataAvailabilityCheckerInner<T> {
         }
 
         pending_components.reconstruction_started = true;
-        ReconstructColumnsDecision::Yes(pending_components.clone())
+        ReconstructColumnsDecision::Yes(pending_components.clone_without_column_recv())
     }
 
     /// This could mean some invalid data columns made it through to the `DataAvailabilityChecker`.
@@ -619,8 +657,9 @@ impl<T: BeaconChainTypes> DataAvailabilityCheckerInner<T> {
 
         // Check if we have all components and entire set is consistent.
         if pending_components.is_available(self.sampling_column_count, log) {
-            write_lock.put(block_root, pending_components.clone());
-            // No need to hold the write lock anymore
+            // We keep the pending components in the availability cache during block import (#5845).
+            // `data_column_recv` is returned as part of the available block and is no longer needed here.
+            write_lock.put(block_root, pending_components.clone_without_column_recv());
             drop(write_lock);
             pending_components.make_available(&self.spec, |diet_block| {
                 self.state_cache.recover_pending_executed_block(diet_block)
@@ -855,6 +894,7 @@ mod test {
             parent_eth1_finalization_data,
             confirmed_state_roots: vec![],
             consensus_context,
+            data_column_recv: None,
         };
 
         let payload_verification_outcome = PayloadVerificationOutcome {
@@ -957,7 +997,7 @@ mod test {
         for (blob_index, gossip_blob) in blobs.into_iter().enumerate() {
             kzg_verified_blobs.push(gossip_blob.into_inner());
             let availability = cache
-                .put_kzg_verified_blobs(root, kzg_verified_blobs.clone(), harness.logger())
+                .put_kzg_verified_blobs(root, kzg_verified_blobs.clone(), None, harness.logger())
                 .expect("should put blob");
             if blob_index == blobs_expected - 1 {
                 assert!(matches!(availability, Availability::Available(_)));
@@ -985,7 +1025,7 @@ mod test {
         for gossip_blob in blobs {
             kzg_verified_blobs.push(gossip_blob.into_inner());
             let availability = cache
-                .put_kzg_verified_blobs(root, kzg_verified_blobs.clone(), harness.logger())
+                .put_kzg_verified_blobs(root, kzg_verified_blobs.clone(), None, harness.logger())
                 .expect("should put blob");
             assert_eq!(
                 availability,
@@ -1241,6 +1281,7 @@ mod pending_components_tests {
                 },
                 confirmed_state_roots: vec![],
                 consensus_context: ConsensusContext::new(Slot::new(0)),
+                data_column_recv: None,
             },
             payload_verification_outcome: PayloadVerificationOutcome {
                 payload_verification_status: PayloadVerificationStatus::Verified,
```

### beacon_node/beacon_chain/src/data_availability_checker/state_lru_cache.rs
```diff
@@ -136,6 +136,7 @@ impl<T: BeaconChainTypes> StateLRUCache<T> {
                 consensus_context: diet_executed_block
                     .consensus_context
                     .into_consensus_context(),
+                data_column_recv: None,
             },
             payload_verification_outcome: diet_executed_block.payload_verification_outcome,
         })
```

### beacon_node/beacon_chain/src/fetch_blobs.rs
```diff
@@ -18,7 +18,7 @@ use slog::{debug, error, o, Logger};
 use ssz_types::FixedVector;
 use state_processing::per_block_processing::deneb::kzg_commitment_to_versioned_hash;
 use std::sync::Arc;
-use tokio::sync::mpsc::Receiver;
+use tokio::sync::oneshot;
 use types::blob_sidecar::{BlobSidecarError, FixedBlobSidecarList};
 use types::{
     BeaconStateError, BlobSidecar, ChainSpec, DataColumnSidecar, DataColumnSidecarList, EthSpec,
@@ -213,9 +213,9 @@ fn spawn_compute_and_publish_data_columns_task<T: BeaconChainTypes>(
     blobs: FixedBlobSidecarList<T::EthSpec>,
     publish_fn: impl Fn(BlobsOrDataColumns<T>) + Send + 'static,
     log: Logger,
-) -> Receiver<Vec<Arc<DataColumnSidecar<T::EthSpec>>>> {
+) -> oneshot::Receiver<Vec<Arc<DataColumnSidecar<T::EthSpec>>>> {
     let chain_cloned = chain.clone();
-    let (data_columns_sender, data_columns_receiver) = tokio::sync::mpsc::channel(1);
+    let (data_columns_sender, data_columns_receiver) = oneshot::channel();
 
     chain.task_executor.spawn_blocking(
         move || {
@@ -248,7 +248,7 @@ fn spawn_compute_and_publish_data_columns_task<T: BeaconChainTypes>(
                 }
             };
 
-            if let Err(e) = data_columns_sender.try_send(all_data_columns.clone()) {
+            if let Err(e) = data_columns_sender.send(all_data_columns.clone()) {
                 error!(log, "Failed to send computed data columns"; "error" => ?e);
             };
 
```

### beacon_node/beacon_chain/tests/block_verification.rs
```diff
@@ -1737,7 +1737,7 @@ async fn import_execution_pending_block<T: BeaconChainTypes>(
         .unwrap()
     {
         ExecutedBlock::Available(block) => chain
-            .import_available_block(Box::from(block), None)
+            .import_available_block(Box::from(block))
             .await
             .map_err(|e| format!("{e:?}")),
         ExecutedBlock::AvailabilityPending(_) => {
```
