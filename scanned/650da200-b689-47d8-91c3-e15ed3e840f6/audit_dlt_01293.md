# [?] Prevent Overflow LRU Cache from Exploding (#4801)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2023-10-11
Source: https://github.com/sigp/lighthouse/commit/8660043024f95a31db9b0027a2e9eacc28d7e727
Type: security-commit

## Details
Prevent Overflow LRU Cache from Exploding (#4801)

* Initial Commit of State LRU Cache

* Build State Caches After Reconstruction

* Cleanup Duplicated Code in OverflowLRUCache Tests

* Added Test for State LRU Cache

* Prune Cache of Old States During Maintenance

* Address Michael's Comments

* Few More Comments

* Removed Unused impl

* Last touch up

* Fix Clippy

## Patch
### beacon_node/beacon_chain/src/block_verification_types.rs
```diff
@@ -5,15 +5,10 @@ pub use crate::data_availability_checker::{AvailableBlock, MaybeAvailableBlock};
 use crate::eth1_finalization_cache::Eth1FinalizationData;
 use crate::{get_block_root, GossipVerifiedBlock, PayloadVerificationOutcome};
 use derivative::Derivative;
-use ssz_derive::{Decode, Encode};
 use ssz_types::VariableList;
 use state_processing::ConsensusContext;
 use std::sync::Arc;
-use types::blob_sidecar::FixedBlobSidecarList;
-use types::{
-    blob_sidecar::BlobIdentifier, ssz_tagged_beacon_state, ssz_tagged_signed_beacon_block,
-    ssz_tagged_signed_beacon_block_arc,
-};
+use types::blob_sidecar::{BlobIdentifier, FixedBlobSidecarList};
 use types::{
     BeaconBlockRef, BeaconState, BlindedPayload, BlobSidecarList, Epoch, EthSpec, Hash256,
     SignedBeaconBlock, SignedBeaconBlockHeader, Slot,
@@ -251,9 +246,7 @@ impl<E: EthSpec> AvailableExecutedBlock<E> {
 /// A block that has completed all pre-deneb block processing checks, verification
 /// by an EL client but does not have all requisite blob data to get imported into
 /// fork choice.
-#[derive(Encode, Decode, Clone)]
 pub struct AvailabilityPendingExecutedBlock<E: EthSpec> {
-    #[ssz(with = "ssz_tagged_signed_beacon_block_arc")]
     pub block: Arc<SignedBeaconBlock<E>>,
     pub import_data: BlockImportData<E>,
     pub payload_verification_outcome: PayloadVerificationOutcome,
@@ -285,14 +278,10 @@ impl<E: EthSpec> AvailabilityPendingExecutedBlock<E> {
     }
 }
 
-#[derive(Debug, PartialEq, Encode, Decode, Clone)]
-// TODO (mark): investigate using an Arc<state> / Arc<parent_block>
-//              here to make this cheaper to clone
+#[derive(Debug, PartialEq)]
 pub struct BlockImportData<E: EthSpec> {
     pub block_root: Hash256,
-    #[ssz(with = "ssz_tagged_beacon_state")]
     pub state: BeaconState<E>,
-    #[ssz(with = "ssz_tagged_signed_beacon_block")]
     pub parent_block: SignedBeaconBlock<E, BlindedPayload<E>>,
     pub parent_eth1_finalization_data: Eth1FinalizationData,
     pub confirmed_state_roots: Vec<Hash256>,
```

### beacon_node/beacon_chain/src/data_availability_checker.rs
```diff
@@ -10,17 +10,14 @@ use crate::data_availability_checker::overflow_lru_cache::OverflowLRUCache;
 use crate::data_availability_checker::processing_cache::ProcessingCache;
 use crate::{BeaconChain, BeaconChainTypes, BeaconStore};
 use kzg::Kzg;
-use kzg::{Error as KzgError, KzgCommitment};
 use parking_lot::RwLock;
 pub use processing_cache::ProcessingComponents;
 use slasher::test_utils::E;
 use slog::{debug, error, Logger};
 use slot_clock::SlotClock;
-use ssz_types::Error;
 use std::fmt;
 use std::fmt::Debug;
 use std::sync::Arc;
-use strum::IntoStaticStr;
 use task_executor::TaskExecutor;
 use types::beacon_block_body::{KzgCommitmentOpts, KzgCommitments};
 use types::blob_sidecar::{BlobIdentifier, BlobSidecar, FixedBlobSidecarList};
@@ -29,54 +26,21 @@ use types::{BlobSidecarList, ChainSpec, Epoch, EthSpec, Hash256, SignedBeaconBlo
 
 mod availability_view;
 mod child_components;
+mod error;
 mod overflow_lru_cache;
 mod processing_cache;
+mod state_lru_cache;
+
+pub use error::{Error as AvailabilityCheckError, ErrorCategory as AvailabilityCheckErrorCategory};
 
 /// The LRU Cache stores `PendingComponents` which can store up to
 /// `MAX_BLOBS_PER_BLOCK = 6` blobs each. A `BlobSidecar` is 0.131256 MB. So
 /// the maximum size of a `PendingComponents` is ~ 0.787536 MB. Setting this
 /// to 1024 means the maximum size of the cache is ~ 0.8 GB. But the cache
 /// will target a size of less than 75% of capacity.
 pub const OVERFLOW_LRU_CAPACITY: usize = 1024;
-
-#[derive(Debug, IntoStaticStr)]
-pub enum AvailabilityCheckError {
-    Kzg(KzgError),
-    KzgNotInitialized,
-    KzgVerificationFailed,
-    KzgCommitmentMismatch {
-        blob_commitment: KzgCommitment,
-        block_commitment: KzgCommitment,
-    },
-    Unexpected,
-    SszTypes(ssz_types::Error),
-    MissingBlobs,
-    BlobIndexInvalid(u64),
-    StoreError(store::Error),
-    DecodeError(ssz::DecodeError),
-    InconsistentBlobBlockRoots {
-        block_root: Hash256,
-        blob_block_root: Hash256,
-    },
-}
-
-impl From<ssz_types::Error> for AvailabilityCheckError {
-    fn from(value: Error) -> Self {
-        Self::SszTypes(value)
-    }
-}
-
-impl From<store::Error> for AvailabilityCheckError {
-    fn from(value: store::Error) -> Self {
-        Self::StoreError(value)
-    }
-}
-
-impl From<ssz::DecodeError> for AvailabilityCheckError {
-    fn from(value: ssz::DecodeError) -> Self {
-        Self::DecodeError(value)
-    }
-}
+/// Until tree-states is implemented, we can't store very many states in memory :(
+pub const STATE_LRU_CAPACITY: usize = 2;
 
 /// This includes a cache for any blocks or blobs that have been received over gossip or RPC
 /// and are awaiting more components before they can be imported. Additionally the
@@ -120,7 +84,7 @@ impl<T: BeaconChainTypes> DataAvailabilityChecker<T> {
         log: &Logger,
         spec: ChainSpec,
     ) -> Result<Self, AvailabilityCheckError> {
-        let overflow_cache = OverflowLRUCache::new(OVERFLOW_LRU_CAPACITY, store)?;
+        let overflow_cache = OverflowLRUCache::new(OVERFLOW_LRU_CAPACITY, store, spec.clone())?;
         Ok(Self {
             processing_cache: <_>::default(),
             availability_cache: Arc::new(overflow_cache),
```

### beacon_node/beacon_chain/src/data_availability_checker/availability_view.rs
```diff
@@ -1,9 +1,9 @@
 use super::child_components::ChildComponents;
+use super::state_lru_cache::DietAvailabilityPendingExecutedBlock;
 use crate::blob_verification::KzgVerifiedBlob;
 use crate::block_verification_types::AsBlock;
 use crate::data_availability_checker::overflow_lru_cache::PendingComponents;
 use crate::data_availability_checker::ProcessingComponents;
-use crate::AvailabilityPendingExecutedBlock;
 use kzg::KzgCommitment;
 use ssz_types::FixedVector;
 use std::sync::Arc;
@@ -190,7 +190,7 @@ impl_availability_view!(
 
 impl_availability_view!(
     PendingComponents,
-    AvailabilityPendingExecutedBlock<E>,
+    DietAvailabilityPendingExecutedBlock<E>,
     KzgVerifiedBlob<E>,
     executed_block,
     verified_blobs
@@ -225,7 +225,7 @@ impl<E: EthSpec> GetCommitment<E> for KzgCommitment {
 }
 
 // These implementations are required to implement `AvailabilityView` for `PendingComponents`.
-impl<E: EthSpec> GetCommitments<E> for AvailabilityPendingExecutedBlock<E> {
+impl<E: EthSpec> GetCommitments<E> for DietAvailabilityPendingExecutedBlock<E> {
     fn get_commitments(&self) -> KzgCommitments<E> {
         self.as_block()
             .message()
@@ -235,6 +235,7 @@ impl<E: EthSpec> GetCommitments<E> for AvailabilityPendingExecutedBlock<E> {
             .unwrap_or_default()
     }
 }
+
 impl<E: EthSpec> GetCommitment<E> for KzgVerifiedBlob<E> {
     fn get_commitment(&self) -> &KzgCommitment {
         &self.as_blob().kzg_commitment
@@ -264,6 +265,7 @@ pub mod tests {
     use crate::block_verification_types::BlockImportData;
     use crate::eth1_finalization_cache::Eth1FinalizationData;
     use crate::test_utils::{generate_rand_block_and_blobs, NumBlobs};
+    use crate::AvailabilityPendingExecutedBlock;
     use crate::PayloadVerificationOutcome;
     use eth2_network_config::get_trusted_setup;
     use fork_choice::PayloadVerificationStatus;
@@ -346,7 +348,7 @@ pub mod tests {
     }
 
     type PendingComponentsSetup<E> = (
-        AvailabilityPendingExecutedBlock<E>,
+        DietAvailabilityPendingExecutedBlock<E>,
         FixedVector<Option<KzgVerifiedBlob<E>>, <E as EthSpec>::MaxBlobsPerBlock>,
         FixedVector<Option<KzgVerifiedBlob<E>>, <E as EthSpec>::MaxBlobsPerBlock>,
     );
@@ -395,7 +397,7 @@ pub mod tests {
                 is_valid_merge_transition_block: false,
             },
         };
-        (block, blobs, invalid_blobs)
+        (block.into(), blobs, invalid_blobs)
     }
 
     type ChildComponentsSetup<E> = (
```

### beacon_node/beacon_chain/src/data_availability_checker/error.rs
```diff
@@ -0,0 +1,79 @@
+use kzg::{Error as KzgError, KzgCommitment};
+use strum::IntoStaticStr;
+use types::{BeaconStateError, Hash256};
+
+#[derive(Debug, IntoStaticStr)]
+pub enum Error {
+    Kzg(KzgError),
+    KzgNotInitialized,
+    KzgVerificationFailed,
+    KzgCommitmentMismatch {
+        blob_commitment: KzgCommitment,
+        block_commitment: KzgCommitment,
+    },
+    Unexpected,
+    SszTypes(ssz_types::Error),
+    MissingBlobs,
+    BlobIndexInvalid(u64),
+    StoreError(store::Error),
+    DecodeError(ssz::DecodeError),
+    InconsistentBlobBlockRoots {
+        block_root: Hash256,
+        blob_block_root: Hash256,
+    },
+    ParentStateMissing(Hash256),
+    BlockReplayError(state_processing::BlockReplayError),
+    RebuildingStateCaches(BeaconStateError),
+}
+
+pub enum ErrorCategory {
+    /// Internal Errors (not caused by peers)
+    Internal,
+    /// Errors caused by faulty / malicious peers
+    Malicious,
+}
+
+impl Error {
+    pub fn category(&self) -> ErrorCategory {
+        match self {
+            Error::KzgNotInitialized
+            | Error::SszTypes(_)
+            | Error::MissingBlobs
+            | Error::StoreError(_)
+            | Error::DecodeError(_)
+            | Error::Unexpected
+            | Error::ParentStateMissing(_)
+            | Error::BlockReplayError(_)
+            | Error::RebuildingStateCaches(_) => ErrorCategory::Internal,
+            Error::Kzg(_)
+            | Error::BlobIndexInvalid(_)
+            | Error::KzgCommitmentMismatch { .. }
+            | Error::KzgVerificationFailed
+            | Error::InconsistentBlobBlockRoots { .. } => ErrorCategory::Malicious,
+        }
+    }
+}
+
+impl From<ssz_types::Error> for Error {
+    fn from(value: ssz_types::Error) -> Self {
+        Self::SszTypes(value)
+    }
+}
+
+impl From<store::Error> for Error {
+    fn from(value: store::Error) -> Self {
+        Self::StoreError(value)
+    }
+}
+
+impl From<ssz::DecodeError> for Error {
+    fn from(value: ssz::DecodeError) -> Self {
+        Self::DecodeError(value)
+    }
+}
+
+impl From<state_processing::BlockReplayError> for Error {
+    fn from(value: state_processing::BlockReplayError) -> Self {
+        Self::BlockReplayError(value)
+    }
+}
```

### beacon_node/beacon_chain/src/data_availability_checker/overflow_lru_cache.rs
```diff
@@ -27,10 +27,11 @@
 //! On startup, the keys of these components are stored in memory and will be loaded in
 //! the cache when they are accessed.
 
+use super::state_lru_cache::{DietAvailabilityPendingExecutedBlock, StateLRUCache};
 use crate::beacon_chain::BeaconStore;
 use crate::blob_verification::KzgVerifiedBlob;
 use crate::block_verification_types::{
-    AsBlock, AvailabilityPendingExecutedBlock, AvailableBlock, AvailableExecutedBlock,
+    AvailabilityPendingExecutedBlock, AvailableBlock, AvailableExecutedBlock,
 };
 use crate::data_availability_checker::availability_view::AvailabilityView;
 use crate::data_availability_checker::{Availability, AvailabilityCheckError};
@@ -43,7 +44,7 @@ use ssz_derive::{Decode, Encode};
 use ssz_types::{FixedVector, VariableList};
 use std::{collections::HashSet, sync::Arc};
 use types::blob_sidecar::BlobIdentifier;
-use types::{BlobSidecar, Epoch, EthSpec, Hash256};
+use types::{BlobSidecar, ChainSpec, Epoch, EthSpec, Hash256};
 
 /// This represents the components of a partially available block
 ///
@@ -53,7 +54,7 @@ use types::{BlobSidecar, Epoch, EthSpec, Hash256};
 pub struct PendingComponents<T: EthSpec> {
     pub block_root: Hash256,
     pub verified_blobs: FixedVector<Option<KzgVerifiedBlob<T>>, T::MaxBlobsPerBlock>,
-    pub executed_block: Option<AvailabilityPendingExecutedBlock<T>>,
+    pub executed_block: Option<DietAvailabilityPendingExecutedBlock<T>>,
 }
 
 impl<T: EthSpec> PendingComponents<T> {
@@ -68,17 +69,25 @@ impl<T: EthSpec> PendingComponents<T> {
     /// Verifies an `SignedBeaconBlock` against a set of KZG verified blobs.
     /// This does not check whether a block *should* have blobs, these checks should have been
     /// completed when producing the `AvailabilityPendingBlock`.
-    pub fn make_available(self) -> Result<Availability<T>, AvailabilityCheckError> {
+    ///
+    /// WARNING: This function can potentially take a lot of time if the state needs to be
+    /// reconstructed from disk. Ensure you are not holding any write locks while calling this.
+    pub fn make_available<R>(self, recover: R) -> Result<Availability<T>, AvailabilityCheckError>
+    where
+        R: FnOnce(
+            DietAvailabilityPendingExecutedBlock<T>,
+        ) -> Result<AvailabilityPendingExecutedBlock<T>, AvailabilityCheckError>,
+    {
         let Self {
             block_root,
             verified_blobs,
             executed_block,
         } = self;
 
-        let Some(executed_block) = executed_block else {
+        let Some(diet_executed_block) = executed_block else {
             return Err(AvailabilityCheckError::Unexpected);
         };
-        let num_blobs_expected = executed_block.num_blobs_expected();
+        let num_blobs_expected = diet_executed_block.num_blobs_expected();
         let Some(verified_blobs) = verified_blobs
             .into_iter()
             .cloned()
@@ -90,6 +99,8 @@ impl<T: EthSpec> PendingComponents<T> {
         };
         let verified_blobs = VariableList::new(verified_blobs)?;
 
+        let executed_block = recover(diet_executed_block)?;
+
         let AvailabilityPendingExecutedBlock {
             block,
             import_data,
@@ -109,7 +120,7 @@ impl<T: EthSpec> PendingComponents<T> {
     pub fn epoch(&self) -> Option<Epoch> {
         self.executed_block
             .as_ref()
-            .map(|pending_block| pending_block.block.epoch())
+            .map(|pending_block| pending_block.as_block().epoch())
             .or_else(|| {
                 for maybe_blob in self.verified_blobs.iter() {
                     if maybe_blob.is_some() {
@@ -208,9 +219,10 @@ impl<T: BeaconChainTypes> OverflowStore<T> {
                 OverflowKey::Block(_) => {
                     maybe_pending_components
                         .get_or_insert_with(|| PendingComponents::empty(block_root))
-                        .executed_block = Some(AvailabilityPendingExecutedBlock::from_ssz_bytes(
-                        value_bytes.as_slice(),
-                    )?);
+                        .executed_block =
+                        Some(DietAvailabilityPendingExecutedBlock::from_ssz_bytes(
+                            value_bytes.as_slice(),
+                        )?);
                 }
                 OverflowKey::Blob(_, index) => {
                     *maybe_pending_components
@@ -356,6 +368,9 @@ pub struct OverflowLRUCache<T: BeaconChainTypes> {
     critical: RwLock<Critical<T>>,
     /// This is how we read and write components to the disk
     overflow_store: OverflowStore<T>,
+    /// This cache holds a limited number of states in memory and reconstructs them
+    /// from disk when necessary. This is necessary until we merge tree-states
+    state_cache: StateLRUCache<T>,
     /// Mutex to guard maintenance methods which move data between disk and memory
     maintenance_lock: Mutex<()>,
     /// The capacity of the LRU cache
@@ -366,13 +381,15 @@ impl<T: BeaconChainTypes> OverflowLRUCache<T> {
     pub fn new(
         capacity: usize,
         beacon_store: BeaconStore<T>,
+        spec: ChainSpec,
     ) -> Result<Self, AvailabilityCheckError> {
-        let overflow_store = OverflowStore(beacon_store);
+        let overflow_store = OverflowStore(beacon_store.clone());
         let mut critical = Critical::new(capacity);
         critical.reload_store_keys(&overflow_store)?;
         Ok(Self {
             critical: RwLock::new(critical),
             overflow_store,
+            state_cache: StateLRUCache::new(beacon_store, spec),
             maintenance_lock: Mutex::new(()),
             capacity,
         })
@@ -426,7 +443,11 @@ impl<T: BeaconChainTypes> OverflowLRUCache<T> {
         pending_components.merge_blobs(fixed_blobs);
 
         if pending_components.is_available() {
-            pending_components.make_available()
+            // No need to hold the write lock anymore
+            drop(write_lock);
+            pending_components.make_available(|diet_block| {
+                self.state_cache.recover_pending_executed_block(diet_block)
+            })
         } else {
             write_lock.put_pending_components(
                 block_root,
@@ -446,17 +467,26 @@ impl<T: BeaconChainTypes> OverflowLRUCache<T> {
         let mut write_lock = self.critical.write();
         let block_root = executed_block.import_data.block_root;
 
+        // register the block to get the diet block
+        let diet_executed_block = self
+            .state_cache
+            .register_pending_executed_block(executed_block);
+
         // Grab existing entry or create a new entry.
         let mut pending_components = write_lock
             .pop_pending_components(block_root, &self.overflow_store)?
             .unwrap_or_else(|| PendingComponents::empty(block_root));
 
         // Merge in the block.
-        pending_components.merge_block(executed_block);
+        pending_components.merge_block(diet_executed_block);
 
         // Check if we have all components and entire set is consistent.
         if pending_components.is_available() {
-            pending_components.make_available()
+            // No need to hold the write lock anymore
+            drop(write_lock);
+            pending_components.make_available(|diet_block| {
+                self.state_cache.recover_pending_executed_block(diet_block)
+            })
         } else {
             write_lock.put_pending_components(
                 block_root,
@@ -493,6 +523,8 @@ impl<T: BeaconChainTypes> OverflowLRUCache<T> {
         self.maintain_threshold(threshold, cutoff_epoch)?;
         // clean up any keys on the disk that shouldn't be there
         self.prune_disk(cutoff_epoch)?;
+        // clean up any lingering states in the state cache
+        self.state_cache.do_maintenance(cutoff_epoch);
         Ok(())
     }
 
@@ -612,10 +644,10 @@ impl<T: BeaconChainTypes> OverflowLRUCache<T> {
                     delete_if_outdated(self, current_block_data)?;
                     let current_epoch = match &overflow_key {
                         OverflowKey::Block(_) => {
-                            AvailabilityPendingExecutedBlock::<T::EthSpec>::from_ssz_bytes(
+                            DietAvailabilityPendingExecutedBlock::<T::EthSpec>::from_ssz_bytes(
                                 value_bytes.as_slice(),
                             )?
-                            .block
+                            .as_block()
                             .epoch()
                         }
                         OverflowKey::Blob(_, _) => {
@@ -639,6 +671,12 @@ impl<T: BeaconChainTypes> OverflowLRUCache<T> {
         drop(maintenance_lock);
         Ok(())
     }
+
+    #[cfg(test)]
+    /// get the state cache for inspection (used only for tests)
+    pub fn state_lru_cache(&self) -> &StateLRUCache<T> {
+        &self.state_cache
+    }
 }
 
 impl ssz::Encode for OverflowKey {
@@ -711,11 +749,11 @@ mod test {
             validate_blob_sidecar_for_gossip, verify_kzg_for_blob, GossipVerifiedBlob,
         },
         block_verification::PayloadVerificationOutcome,
-        block_verification_types::BlockImportData,
+        block_verification_types::{AsBlock, BlockImportData},
+        data_availability_checker::STATE_LRU_CAPACITY,
         eth1_finalization_cache::Eth1FinalizationData,
         test_utils::{BaseHarnessType, BeaconChainHarness, DiskHarnessType},
     };
-    use execution_layer::test_utils::DEFAULT_TERMINAL_BLOCK;
     use fork_choice::PayloadVerificationStatus;
     use logging::test_logger;
     use slog::{info, Logger};
@@ -724,7 +762,6 @@ mod test {
     use std::ops::AddAssign;
     use store::{HotColdDB, ItemStore, LevelDB, StoreConfig};
     use tempfile::{tempdir, TempDir};
-    use types::beacon_state::ssz_tagged_beacon_state;
     use types::{ChainSpec, ExecPayload, MinimalEthSpec};
 
     const LOW_VALIDATOR_COUNT: usize = 32;
@@ -754,7 +791,7 @@ mod test {
     async fn get_deneb_chain<E: EthSpec>(
         log: Logger,
         db_path: &TempDir,
-    ) -> BeaconChainHarness<BaseHarnessType<E, LevelDB<E>, LevelDB<E>>> {
+    ) -> BeaconChainHarness<DiskHarnessType<E>> {
         let altair_fork_epoch = Epoch::new(1);
         let bellatrix_fork_epoch = Epoch::new(2);
         let bellatrix_fork_slot = bellatrix_fork_epoch.start_slot(E::slots_per_epoch());
@@ -837,91 +874,8 @@ mod test {
         }
     }
 
-    #[tokio::test]
-    async fn ssz_tagged_beacon_state_encode_decode_equality() {
-        type E = MinimalEthSpec;
-        let altair_fork_epoch = Epoch::new(1);
-        let altair_fork_slot = altair_fork_epoch.start_slot(E::slots_per_epoch());
-        let bellatrix_fork_epoch = Epoch::new(2);
-        let merge_fork_slot = bellatrix_fork_epoch.start_slot(E::slots_per_epoch());
-        let capella_fork_epoch = Epoch::new(3);
-        let capella_fork_slot = capella_fork_epoch.start_slot(E::slots_per_epoch());
-        let deneb_fork_epoch = Epoch::new(4);
-        let deneb_fork_slot = deneb_fork_epoch.start_slot(E::slots_per_epoch());
-
-        let mut spec = E::default_spec();
-        spec.altair_fork_epoch = Some(altair_fork_epoch);
-        spec.bellatrix_fork_epoch = Some(bellatrix_fork_epoch);
-        spec.capella_fork_epoch = Some(capella_fork_epoch);
-        spec.deneb_fork_epoch = Some(deneb_fork_epoch);
-        let genesis_block = execution_layer::test_utils::generate_genesis_block(
-            spec.terminal_total_difficulty,
-            DEFAULT_TERMINAL_BLOCK,
-        )
-        .unwrap();
-        spec.terminal_block_hash = genesis_block.block_hash;
-        spec.terminal_block_hash_activation_epoch = bellatrix_fork_epoch;
-
-        let harness = BeaconChainHarness::builder(E::default())
-            .spec(spec)
-            .logger(logging::test_logger())
-            .deterministic_keypairs(LOW_VALIDATOR_COUNT)
-            .fresh_ephemeral_store()
-            .mock_execution_layer()
-            .build();
-
-        let mut state = harness.get_current_state();
-        assert!(state.as_base().is_ok());
-        let encoded = ssz_tagged_beacon_state::encode::as_ssz_bytes(&state);
-        let decoded =
-            ssz_tagged_beacon_state::decode::from_ssz_bytes(&encoded).expect("should decode");
-        state.drop_all_caches().expect("should drop caches");
-        assert_eq!(state, decoded, "Encoded and decoded states should be equal");
-
-        harness.extend_to_slot(altair_fork_slot).await;
-
-        let mut state = harness.get_current_state();
-        assert!(state.as_altair().is_ok());
-        let encoded = ssz_tagged_beacon_state::encode::as_ssz_bytes(&state);
-        let decoded =
-            ssz_tagged_beacon_state::decode::from_ssz_bytes(&encoded).expect("should decode");
-        state.drop_all_caches().expect("should drop caches");
-        assert_eq!(state, decoded, "Encoded and decoded states should be equal");
-
-        harness.extend_to_slot(merge_fork_slot).await;
-
-        let mut state = harness.get_current_state();
-        assert!(state.as_merge().is_ok());
-        let encoded = ssz_tagged_beacon_state::encode::as_ssz_bytes(&state);
-        let decoded =
-            ssz_tagged_beacon_state::decode::from_ssz_bytes(&encoded).expect("should decode");
-        state.drop_all_caches().expect("should drop caches");
-        assert_eq!(state, decoded, "Encoded and decoded states should be equal");
-
-        harness.extend_to_slot(capella_fork_slot).await;
-
-        let mut state = harness.get_current_state();
-        assert!(state.as_capella().is_ok());
-        let encoded = ssz_tagged_beacon_state::encode::as_ssz_bytes(&state);
-        let decoded =
-            ssz_tagged_beacon_state::decode::from_ssz_bytes(&encoded).expect("should decode");
-        state.drop_all_caches().expect("should drop caches");
-        assert_eq!(state, decoded, "Encoded and decoded states should be equal");
-
-        harness.extend_to_slot(deneb_fork_slot).await;
-
-        let mut state = harness.get_current_state();
-        assert!(state.as_deneb().is_ok());
-        let encoded = ssz_tagged_beacon_state::encode::as_ssz_bytes(&state);
-        let decoded =
-            ssz_tagged_beacon_state::decode::from_ssz_bytes(&encoded).expect("should decode");
-        state.drop_all_caches().expect("should drop caches");
-        assert_eq!(state, decoded, "Encoded and decoded states should be equal");
-    }
-
     async fn availability_pending_block<E, Hot, Cold>(
         harness: &BeaconChainHarness<BaseHarnessType<E, Hot, Cold>>,
-        log: Logger,
     ) -> (
         AvailabilityPendingExecutedBlock<E>,
         Vec<GossipVerifiedBlob<BaseHarnessType<E, Hot, Cold>>>,
@@ -932,6 +886,7 @@ mod test {
         Cold: ItemStore<E>,
     {
         let chain = &harness.chain;
+        let log = chain.log.clone();
         let head = chain.head_snapshot();
         let parent_state = head.beacon_state.clone_with_only_committee_caches();
 
@@ -1010,22 +965,36 @@ mod test {
         (availability_pending_block, gossip_verified_blobs)
     }
 
-    #[tokio::test]
-    async fn overflow_cache_test_insert_components() {
-        type E = MinimalEthSpec;
-        type T = DiskHarnessType<E>;
+    async fn setup_harness_and_cache<E, T>(
+        capacity: usize,
+    ) -> (
+        BeaconChainHarness<DiskHarnessType<E>>,
+        Arc<OverflowLRUCache<T>>,
+    )
+    where
+        E: EthSpec,
+        T: BeaconChainTypes<HotStore = LevelDB<E>, ColdStore = LevelDB<E>, EthSpec = E>,
+    {
         let log = test_logger();
         let chain_db_path = tempdir().expect("should get temp dir");
-        let harness: BeaconChainHarness<T> = get_deneb_chain(log.clone(), &chain_db_path).await;
+        let harness = get_deneb_chain(log.clone(), &chain_db_path).await;
         let spec = harness.spec.clone();
-        let capacity = 4;
-        let db_path = tempdir().expect("should get temp dir");
-        let test_store = get_store_with_spec::<E>(&db_path, spec.clone(), log.clone());
+        let test_store = harness.chain.store.clone();
         let cache = Arc::new(
-            OverflowLRUCache::<T>::new(capacity, test_store).expect("should create cache"),
+            OverflowLRUCache::<T>::new(capacity, test_store, spec.clone())
+                .expect("should create cache"),
         );
+        (harness, cache)
+    }
+
+    #[tokio::test]
+    async fn overflow_cache_test_insert_components() {
+        type E = MinimalEthSpec;
+        type T = DiskHarnessType<E>;
+        let capacity = 4;
+        let (harness, cache) = setup_harness_and_cache::<E, T>(capacity).await;
 
-        let (pending_block, blobs) = availability_pending_block(&harness, log.clone()).await;
+        let (pending_block, blobs) = availability_pending_block(&harness).await;
         let root = pending_block.import_data.block_root;
 
         let blobs_expected = pending_block.num_blobs_expected();
@@ -1093,7 +1062,7 @@ mod test {
             "cache should be empty now that all components available"
         );
 
-        let (pending_block, blobs) = availability_pending_block(&harness, log.clone()).await;
+        let (pending_block, blobs) = availability_pending_block(&harness).await;
         let blobs_expected = pending_block.num_blobs_expected();
         assert_eq!(
             blobs.len(),
@@ -1134,22 +1103,14 @@ mod test {
     async fn overflow_cache_test_overflow() {
         type E = MinimalEthSpec;
         type T = DiskHarnessType<E>;
-        let log = test_logger();
-        let chain_db_path = tempdir().expect("should get temp dir");
-        let harness: BeaconChainHarness<T> = get_deneb_chain(log.clone(), &chain_db_path).await;
-        let spec = harness.spec.clone();
         let capacity = 4;
-        let db_path = tempdir().expect("should get temp dir");
-        let test_store = get_store_with_spec::<E>(&db_path, spec.clone(), log.clone());
-        let cache = Arc::new(
-            OverflowLRUCache::<T>::new(capacity, test_store).expect("should create cache"),
-        );
+        let (harness, cache) = setup_harness_and_cache::<E, T>(capacity).await;
 
         let mut pending_blocks = VecDeque::new();
         let mut pending_blobs = VecDeque::new();
         let mut roots = VecDeque::new();
         while pending_blobs.len() < capacity + 1 {
-            let (pending_block, blobs) = availability_pending_block(&harness, log.clone()).await;
+            let (pending_block, blobs) = availability_pending_block(&harness).await;
             if pending_block.num_blobs_expected() == 0 {
                 // we need blocks with blobs
                 continue;
@@ -1293,29 +1254,19 @@ mod test {
     async fn overflow_cache_test_maintenance() {
         type E = MinimalEthSpec;
         type T = DiskHarnessType<E>;
-        let log = test_logger();
-        let chain_db_path = tempdir().expect("should get temp dir");
-        let harness: BeaconChainHarness<T> = get_deneb_chain(log.clone(), &chain_db_path).await;
-        let spec = harness.spec.clone();
-        let n_epochs = 4;
         let capacity = E::slots_per_epoch() as usize;
-        let db_path = tempdir().expect("should get temp dir");
-        let test_store = get_store_with_spec::<E>(&db_path, spec.clone(), log.clone());
-        let cache = Arc::new(
-            OverflowLRUCache::<T>::new(capacity, test_store).expect("should create cache"),
-        );
+        let (harness, cache) = setup_harness_and_cache::<E, T>(capacity).await;
 
+        let n_epochs = 4;
         let mut pending_blocks = VecDeque::new();
         let mut pending_blobs = VecDeque::new();
-        let mut roots = VecDeque::new();
         let mut epoch_count = BTreeMap::new();
         while pending_blobs.len() < n_epochs * capacity {
-            let (pending_block, blobs) = availability_pending_block(&harness, log.clone()).await;
+            let (pending_block, blobs) = availability_pending_block(&harness).await;
             if pending_block.num_blobs_expected() == 0 {
                 // we need blocks with blobs
                 continue;
             }
-            let root = pending_block.block.canonical_root();
             let epoch = pending_block
                 .block
                 .as_block()
@@ -1325,7 +1276,6 @@ mod test {
 
             pending_blocks.push_back(pending_block);
             pending_blobs.push_back(blobs);
-            roots.push_back(root);
         }
 
         let kzg = harness
@@ -1424,7 +1374,7 @@ mod test {
             let mem_keys = cache.critical.read().in_memory.len();
             expected_length -= count;
             info!(
-                log,
+                harness.chain.log,
                 "EPOCH: {} DISK KEYS: {} MEM KEYS: {} TOTAL: {} EXPECTED: {}",
                 epoch,
                 disk_keys,
@@ -1444,29 +1394,19 @@ mod test {
     async fn overflow_cache_test_persist_recover() {
         type E = MinimalEthSpec;
         type T = DiskHarnessType<E>;
-        let log = test_logger();
-        let chain_db_path = tempdir().expect("should get temp dir");
-        let harness: BeaconChainHarness<T> = get_deneb_chain(log.clone(), &chain_db_path).await;
-        let spec = harness.spec.clone();
-        let n_epochs = 4;
         let capacity = E::slots_per_epoch() as usize;
-        let db_path = tempdir().expect("should get temp dir");
-        let test_store = get_store_with_spec::<E>(&db_path, spec.clone(), log.clone());
-        let cache = Arc::new(
-            OverflowLRUCache::<T>::new(capacity, test_store.clone()).expect("should create cache"),
-        );
+        let (harness, cache) = setup_harness_and_cache::<E, T>(capacity).await;
 
+        let n_epochs = 4;
         let mut pending_blocks = VecDeque::new();
         let mut pending_blobs = VecDeque::new();
-        let mut roots = VecDeque::new();
         let mut epoch_count = BTreeMap::new();
         while pending_blobs.len() < n_epochs * capacity {
-            let (pending_block, blobs) = availability_pending_block(&harness, log.clone()).await;
+            let (pending_block, blobs) = availability_pending_block(&harness).await;
             if pending_block.num_blobs_expected() == 0 {
                 // we need blocks with blobs
                 continue;
             }
-            let root = pending_block.block.as_block().canonical_root();
             let epoch = pending_block
                 .block
                 .as_block()
@@ -1476,7 +1416,6 @@ mod test {
 
             pending_blocks.push_back(pending_block);
             pending_blobs.push_back(blobs);
-            roots.push_back(root);
         }
 
         let kzg = harness
@@ -1580,8 +1519,12 @@ mod test {
         drop(cache);
 
         // create a new cache with the same store
-        let recovered_cache =
-            OverflowLRUCache::<T>::new(capacity, test_store).expect("should recover cache");
+        let recovered_cache = OverflowLRUCache::<T>::new(
+            capacity,
+            harness.chain.store.clone(),
+            harness.chain.spec.clone(),
+        )
+        .expect("should recover cache");
         // again, everything should be on disk
         assert_eq!(
             recovered_cache
@@ -1622,4 +1565,133 @@ mod test {
             }
         }
     }
+
+    #[tokio::test]
+    // ensure the state cache keeps memory usage low and that it can properly recover states
+    // THIS TEST CAN BE DELETED ONCE TREE STATES IS MERGED AND WE RIP OUT THE STATE CACHE
+    async fn overflow_cache_test_state_cache() {
+        type E = MinimalEthSpec;
+        type T = DiskHarnessType<E>;
+        let capacity = STATE_LRU_CAPACITY * 2;
+        let (harness, cache) = setup_harness_and_cache::<E, T>(capacity).await;
+
+        let mut pending_blocks = VecDeque::new();
+        let mut states = Vec::new();
+        let mut state_roots = Vec::new();
+        // Get enough blocks to fill the cache to capacity, ensuring all blocks have blobs
+        while pending_blocks.len() < capacity {
+            let (pending_block, _) = availability_pending_block(&harness).await;
+            if pending_block.num_blobs_expected() == 0 {
+                // we need blocks with blobs
+                continue;
+            }
+            let state_root = pending_block.import_data.state.canonical_root();
+            states.push(pending_block.import_data.state.clone());
+            pending_blocks.push_back(pending_block);
+            state_roots.push(state_root);
+        }
+
+        let state_cache = cache.state_lru_cache().lru_cache();
+        let mut pushed_diet_blocks = VecDeque::new();
+
+        for i in 0..capacity {
+            let pending_block = pending_blocks.pop_front().expect("should have block");
+            let block_root = pending_block.as_block().canonical_root();
+
+            assert_eq!(
+                state_cache.read().len(),
+                std::cmp::min(i, STATE_LRU_CAPACITY),
+                "state cache should be empty at start"
+            );
+
+            if i >= STATE_LRU_CAPACITY {
+                let lru_root = state_roots[i - STATE_LRU_CAPACITY];
+                assert_eq!(
+                    state_cache.read().peek_lru().map(|(root, _)| root),
+                    Some(&lru_root),
+                    "lru block should be in cache"
+                );
+            }
+
+            // put the block in the cache
+            let availability = cache
+                .put_pending_executed_block(pending_block)
+                .expect("should put block");
+
+            // grab the diet block from the cache for later testing
+            let diet_block = cache
+                .critical
+                .read()
+                .in_memory
+                .peek(&block_root)
+                .map(|pending_components| {
+                    pending_components
+                        .executed_block
+                        .clone()
+                        .expect("should exist")
+                })
+                .expect("should exist");
+            pushed_diet_blocks.push_back(diet_block);
+
+            // should be unavailable since we made sure all blocks had blobs
+            assert!(
+                matches!(availability, Availability::MissingComponents(_)),
+                "should be pending blobs"
+            );
+
+            if i >= STATE_LRU_CAPACITY {
+                let evicted_index = i - STATE_LRU_CAPACITY;
+                let evicted_root = state_roots[evicted_index];
+                assert!(
+                    state_cache.read().peek(&evicted_root).is_none(),
+                    "lru root should be evicted"
+                );
+                // get the diet block via direct conversion (testing only)
+                let diet_block = pushed_diet_blocks.pop_front().expect("should have block");
+                // reconstruct the pending block by replaying the block on the parent state
+                let recovered_pending_block = cache
+                    .state_lru_cache()
+                    .reconstruct_pending_executed_block(diet_block)
+                    .expect("should reconstruct pending block");
+
+                // assert the recovered state is the same as the original
+                assert_eq!(
+                    recovered_pending_block.import_data.state, states[evicted_index],
+                    "recovered state should be the same as the original"
+                );
+            }
+        }
+
+        // now check the last block
+        let last_block = pushed_diet_blocks.pop_back().expect("should exist").clone();
+        // the state should still be in the cache
+        assert!(
+            state_cache
+                .read()
+                .peek(&last_block.as_block().state_root())
+                .is_some(),
+            "last block state should still be in cache"
+        );
+        // get the diet block via direct conversion (testing only)
+        let diet_block = last_block.clone();
+        // recover the pending block from the cache
+        let recovered_pending_block = cache
+            .state_lru_cache()
+            .recover_pending_executed_block(diet_block)
+            .expect("should reconstruct pending block");
+        // assert the recovered state is the same as the original
+        assert_eq!(
+            Some(&recovered_pending_block.import_data.state),
+            states.last(),
+            "recovered state should be the same as the original"
+        );
+        // the state should no longer be in the cache
+        assert!(
+            state_cache
+                .read()
+                .peek(&last_block.as_block().state_root())
+                .is_none(),
+            "last block state should no longer be in cache"
+        );
+    }
 }
```

### beacon_node/beacon_chain/src/data_availability_checker/state_lru_cache.rs
```diff
@@ -0,0 +1,230 @@
+use crate::block_verification_types::AsBlock;
+use crate::{
+    block_verification_types::BlockImportData,
+    data_availability_checker::{AvailabilityCheckError, STATE_LRU_CAPACITY},
+    eth1_finalization_cache::Eth1FinalizationData,
+    AvailabilityPendingExecutedBlock, BeaconChainTypes, BeaconStore, PayloadVerificationOutcome,
+};
+use lru::LruCache;
+use parking_lot::RwLock;
+use ssz_derive::{Decode, Encode};
+use state_processing::{BlockReplayer, ConsensusContext, StateProcessingStrategy};
+use std::sync::Arc;
+use types::{ssz_tagged_signed_beacon_block, ssz_tagged_signed_beacon_block_arc};
+use types::{BeaconState, BlindedPayload, ChainSpec, Epoch, EthSpec, Hash256, SignedBeaconBlock};
+
+/// This mirrors everything in the `AvailabilityPendingExecutedBlock`, except
+/// that it is much smaller because it contains only a state root instead of
+/// a full `BeaconState`.
+#[derive(Encode, Decode, Clone)]
+pub struct DietAvailabilityPendingExecutedBlock<E: EthSpec> {
+    #[ssz(with = "ssz_tagged_signed_beacon_block_arc")]
+    block: Arc<SignedBeaconBlock<E>>,
+    state_root: Hash256,
+    #[ssz(with = "ssz_tagged_signed_beacon_block")]
+    parent_block: SignedBeaconBlock<E, BlindedPayload<E>>,
+    parent_eth1_finalization_data: Eth1FinalizationData,
+    confirmed_state_roots: Vec<Hash256>,
+    consensus_context: ConsensusContext<E>,
+    payload_verification_outcome: PayloadVerificationOutcome,
+}
+
+/// just implementing the same methods as `AvailabilityPendingExecutedBlock`
+impl<E: EthSpec> DietAvailabilityPendingExecutedBlock<E> {
+    pub fn as_block(&self) -> &SignedBeaconBlock<E> {
+        &self.block
+    }
+
+    pub fn num_blobs_expected(&self) -> usize {
+        self.block
+            .message()
+            .body()
+            .blob_kzg_commitments()
+            .map_or(0, |commitments| commitments.len())
+    }
+}
+
+/// This LRU cache holds BeaconStates used for block import. If the cache overflows,
+/// the least recently used state will be dropped. If the dropped state is needed
+/// later on, it will be recovered from the parent state and replaying the block.
+///
+/// WARNING: This cache assumes the parent block of any `AvailabilityPendingExecutedBlock`
+/// has already been imported into ForkChoice. If this is not the case, the cache
+/// will fail to recover the state when the cache overflows because it can't load
+/// the parent state!
+pub struct StateLRUCache<T: BeaconChainTypes> {
+    states: RwLock<LruCache<Hash256, BeaconState<T::EthSpec>>>,
+    store: BeaconStore<T>,
+    spec: ChainSpec,
+}
+
+impl<T: BeaconChainTypes> StateLRUCache<T> {
+    pub fn new(store: BeaconStore<T>, spec: ChainSpec) -> Self {
+        Self {
+            states: RwLock::new(LruCache::new(STATE_LRU_CAPACITY)),
+            store,
+            spec,
+        }
+    }
+
+    /// This will store the state in the LRU cache and return a
+    /// `DietAvailabilityPendingExecutedBlock` which is much cheaper to
+    /// keep around in memory.
+    pub fn register_pending_executed_block(
+        &self,
+        executed_block: AvailabilityPendingExecutedBlock<T::EthSpec>,
+    ) -> DietAvailabilityPendingExecutedBlock<T::EthSpec> {
+        let state = executed_block.import_data.state;
+        let state_root = executed_block.block.state_root();
+        self.states.write().put(state_root, state);
+
+        DietAvailabilityPendingExecutedBlock {
+            block: executed_block.block,
+            state_root,
+            parent_block: executed_block.import_data.parent_block,
+            parent_eth1_finalization_data: executed_block.import_data.parent_eth1_finalization_data,
+            confirmed_state_roots: executed_block.import_data.confirmed_state_roots,
+            consensus_context: executed_block.import_data.consensus_context,
+            payload_verification_outcome: executed_block.payload_verification_outcome,
+        }
+    }
+
+    /// Recover the `AvailabilityPendingExecutedBlock` from the diet version.
+    /// This method will first check the cache and if the state is not found
+    /// it will reconstruct the state by loading the parent state from disk and
+    /// replaying the block.
+    pub fn recover_pending_executed_block(
+        &self,
+        diet_executed_block: DietAvailabilityPendingExecutedBlock<T::EthSpec>,
+    ) -> Result<AvailabilityPendingExecutedBlock<T::EthSpec>, AvailabilityCheckError> {
+        let maybe_state = self.states.write().pop(&diet_executed_block.state_root);
+        if let Some(state) = maybe_state {
+            let block_root = diet_executed_block.block.canonical_root();
+            Ok(AvailabilityPendingExecutedBlock {
+                block: diet_executed_block.block,
+                import_data: BlockImportData {
+                    block_root,
+                    state,
+                    parent_block: diet_executed_block.parent_block,
+                    parent_eth1_finalization_data: diet_executed_block
+                        .parent_eth1_finalization_data,
+                    confirmed_state_roots: diet_executed_block.confirmed_state_roots,
+                    consensus_context: diet_executed_block.consensus_context,
+                },
+                payload_verification_outcome: diet_executed_block.payload_verification_outcome,
+            })
+        } else {
+            self.reconstruct_pending_executed_block(diet_executed_block)
+        }
+    }
+
+    /// Reconstruct the `AvailabilityPendingExecutedBlock` by loading the parent
+    /// state from disk and replaying the block. This function does NOT check the
+    /// LRU cache.
+    pub fn reconstruct_pending_executed_block(
+        &self,
+        diet_executed_block: DietAvailabilityPendingExecutedBlock<T::EthSpec>,
+    ) -> Result<AvailabilityPendingExecutedBlock<T::EthSpec>, AvailabilityCheckError> {
+        let block_root = diet_executed_block.block.canonical_root();
+        let state = self.reconstruct_state(&diet_executed_block)?;
+        Ok(AvailabilityPendingExecutedBlock {
+            block: diet_executed_block.block,
+            import_data: BlockImportData {
+                block_root,
+                state,
+                parent_block: diet_executed_block.parent_block,
+                parent_eth1_finalization_data: diet_executed_block.parent_eth1_finalization_data,
+                confirmed_state_roots: diet_executed_block.confirmed_state_roots,
+                consensus_context: diet_executed_block.consensus_context,
+            },
+            payload_verification_outcome: diet_executed_block.payload_verification_outcome,
+        })
+    }
+
+    /// Reconstruct the state by loading the parent state from disk and replaying
+    /// the block.
+    fn reconstruct_state(
+        &self,
+        diet_executed_block: &DietAvailabilityPendingExecutedBlock<T::EthSpec>,
+    ) -> Result<BeaconState<T::EthSpec>, AvailabilityCheckError> {
+        let parent_block_root = diet_executed_block.parent_block.canonical_root();
+        let parent_block_state_root = diet_executed_block.parent_block.state_root();
+        let (parent_state_root, parent_state) = self
+            .store
+            .get_advanced_hot_state(
+                parent_block_root,
+                diet_executed_block.parent_block.slot(),
+                parent_block_state_root,
+            )
+            .map_err(AvailabilityCheckError::StoreError)?
+            .ok_or(AvailabilityCheckError::ParentStateMissing(
+                parent_block_state_root,
+            ))?;
+
+        let state_roots = vec![
+            Ok((parent_state_root, diet_executed_block.parent_block.slot())),
+            Ok((
+                diet_executed_block.state_root,
+                diet_executed_block.block.slot(),
+            )),
+        ];
+
+        let block_replayer: BlockReplayer<'_, T::EthSpec, AvailabilityCheckError, _> =
+            BlockReplayer::new(parent_state, &self.spec)
+                .no_signature_verification()
+                .state_processing_strategy(StateProcessingStrategy::Accurate)
+                .state_root_iter(state_roots.into_iter())
+                .minimal_block_root_verification();
+
+        block_replayer
+            .apply_blocks(vec![diet_executed_block.block.clone_as_blinded()], None)
+            .map(|block_replayer| block_replayer.into_state())
+            .and_then(|mut state| {
+                state
+                    .build_exit_cache(&self.spec)
+                    .map_err(AvailabilityCheckError::RebuildingStateCaches)?;
+                state
+                    .update_tree_hash_cache()
+                    .map_err(AvailabilityCheckError::RebuildingStateCaches)?;
+                Ok(state)
+            })
+    }
+
+    /// returns the state cache for inspection in tests
+    #[cfg(test)]
+    pub fn lru_cache(&self) -> &RwLock<LruCache<Hash256, BeaconState<T::EthSpec>>> {
+        &self.states
+    }
+
+    /// remove any states from the cache from before the given epoch
+    pub fn do_maintenance(&self, cutoff_epoch: Epoch) {
+        let mut write_lock = self.states.write();
+        while let Some((_, state)) = write_lock.peek_lru() {
+            if state.slot().epoch(T::EthSpec::slots_per_epoch()) < cutoff_epoch {
+                write_lock.pop_lru();
+            } else {
+                break;
+            }
+        }
+    }
+}
+
+/// This can only be used during testing. The intended way to
+/// obtain a `DietAvailabilityPendingExecutedBlock` is to call
+/// `register_pending_executed_block` on the `StateLRUCache`.
+#[cfg(test)]
+impl<E: EthSpec> From<AvailabilityPendingExecutedBlock<E>>
+    for DietAvailabilityPendingExecutedBlock<E>
+{
+    fn from(value: AvailabilityPendingExecutedBlock<E>) -> Self {
+        Self {
+            block: value.block,
+            state_root: value.import_data.state.canonical_root(),
+            parent_block: value.import_data.parent_block,
+            parent_eth1_finalization_data: value.import_data.parent_eth1_finalization_data,
+            confirmed_state_roots: value.import_data.confirmed_state_roots,
+            consensus_context: value.import_data.consensus_context,
+            payload_verification_outcome: value.payload_verification_outcome,
+        }
+    }
+}
```

### beacon_node/network/src/network_beacon_processor/gossip_methods.rs
```diff
@@ -11,7 +11,7 @@ use beacon_chain::block_verification_types::AsBlock;
 use beacon_chain::store::Error;
 use beacon_chain::{
     attestation_verification::{self, Error as AttnError, VerifiedAttestation},
-    data_availability_checker::AvailabilityCheckError,
+    data_availability_checker::AvailabilityCheckErrorCategory,
     light_client_finality_update_verification::Error as LightClientFinalityUpdateError,
     light_client_optimistic_update_verification::Error as LightClientOptimisticUpdateError,
     observed_operations::ObservationOutcome,
@@ -1233,24 +1233,15 @@ impl<T: BeaconChainTypes> NetworkBeaconProcessor<T> {
                 );
             }
             Err(BlockError::AvailabilityCheck(err)) => {
-                match err {
-                    AvailabilityCheckError::KzgNotInitialized
-                    | AvailabilityCheckError::Unexpected
-                    | AvailabilityCheckError::SszTypes(_)
-                    | AvailabilityCheckError::MissingBlobs
-                    | AvailabilityCheckError::StoreError(_)
-                    | AvailabilityCheckError::DecodeError(_) => {
+                match err.category() {
+                    AvailabilityCheckErrorCategory::Internal => {
                         warn!(
                             self.log,
                             "Internal availability check error";
                             "error" => ?err,
                         );
                     }
-                    AvailabilityCheckError::Kzg(_)
-                    | AvailabilityCheckError::KzgVerificationFailed
-                    | AvailabilityCheckError::KzgCommitmentMismatch { .. }
-                    | AvailabilityCheckError::BlobIndexInvalid(_)
-                    | AvailabilityCheckError::InconsistentBlobBlockRoots { .. } => {
+                    AvailabilityCheckErrorCategory::Malicious => {
                         // Note: we cannot penalize the peer that sent us the block
                         // over gossip here because these errors imply either an issue
                         // with:
```

### beacon_node/network/src/sync/block_lookups/mod.rs
```diff
@@ -13,7 +13,9 @@ use crate::sync::block_lookups::single_block_lookup::{
 use crate::sync::manager::{Id, SingleLookupReqId};
 use beacon_chain::block_verification_types::{AsBlock, RpcBlock};
 pub use beacon_chain::data_availability_checker::ChildComponents;
-use beacon_chain::data_availability_checker::{AvailabilityCheckError, DataAvailabilityChecker};
+use beacon_chain::data_availability_checker::{
+    AvailabilityCheckErrorCategory, DataAvailabilityChecker,
+};
 use beacon_chain::validator_monitor::timestamp_now;
 use beacon_chain::{AvailabilityProcessingStatus, BeaconChainTypes, BlockError};
 pub use common::Current;
@@ -893,39 +895,25 @@ impl<T: BeaconChainTypes> BlockLookups<T> {
                 );
                 return Ok(None);
             }
-            BlockError::AvailabilityCheck(e) => {
-                match e {
-                    // Internal error.
-                    AvailabilityCheckError::KzgNotInitialized
-                    | AvailabilityCheckError::SszTypes(_)
-                    | AvailabilityCheckError::MissingBlobs
-                    | AvailabilityCheckError::StoreError(_)
-                    | AvailabilityCheckError::DecodeError(_)
-                    | AvailabilityCheckError::Unexpected => {
-                        warn!(self.log, "Internal availability check failure"; "root" => %root, "peer_id" => %peer_id, "error" => ?e);
-                        lookup
-                            .block_request_state
-                            .state
-                            .register_failure_downloading();
-                        lookup
-                            .blob_request_state
-                            .state
-                            .register_failure_downloading();
-                        lookup.request_block_and_blobs(cx)?
-                    }
-
-                    // Malicious errors.
-                    AvailabilityCheckError::Kzg(_)
-                    | AvailabilityCheckError::BlobIndexInvalid(_)
-                    | AvailabilityCheckError::KzgCommitmentMismatch { .. }
-                    | AvailabilityCheckError::KzgVerificationFailed
-                    | AvailabilityCheckError::InconsistentBlobBlockRoots { .. } => {
-                        warn!(self.log, "Availability check failure"; "root" => %root, "peer_id" => %peer_id, "error" => ?e);
-                        lookup.handle_availability_check_failure(cx);
-                        lookup.request_block_and_blobs(cx)?
-                    }
+            BlockError::AvailabilityCheck(e) => match e.category() {
+                AvailabilityCheckErrorCategory::Internal => {
+                    warn!(self.log, "Internal availability check failure"; "root" => %root, "peer_id" => %peer_id, "error" => ?e);
+                    lookup
+                        .block_request_state
+                        .state
+                        .register_failure_downloading();
+                    lookup
+                        .blob_request_state
+                        .state
+                        .register_failure_downloading();
+                    lookup.request_block_and_blobs(cx)?
                 }
-            }
+                AvailabilityCheckErrorCategory::Malicious => {
+                    warn!(self.log, "Availability check failure"; "root" => %root, "peer_id" => %peer_id, "error" => ?e);
+                    lookup.handle_availability_check_failure(cx);
+                    lookup.request_block_and_blobs(cx)?
+                }
+            },
             other => {
                 warn!(self.log, "Peer sent invalid block in single block lookup"; "root" => %root, "error" => ?other, "peer_id" => %peer_id);
                 if let Ok(block_peer) = lookup.block_request_state.state.processing_peer() {
```

### consensus/types/src/beacon_state.rs
```diff
@@ -1946,80 +1946,3 @@ impl<T: EthSpec> ForkVersionDeserialize for BeaconState<T> {
         ))
     }
 }
-
-/// This module can be used to encode and decode a `BeaconState` the same way it
-/// would be done if we had tagged the superstruct enum with
-/// `#[ssz(enum_behaviour = "union")]`
-/// This should _only_ be used for *some* cases to store these objects in the
-/// database and _NEVER_ for encoding / decoding states sent over the network!
-pub mod ssz_tagged_beacon_state {
-    use super::*;
-    pub mod encode {
-        use super::*;
-        #[allow(unused_imports)]
-        use ssz::*;
-
-        pub fn is_ssz_fixed_len() -> bool {
-            false
-        }
-
-        pub fn ssz_fixed_len() -> usize {
-            BYTES_PER_LENGTH_OFFSET
-        }
-
-        pub fn ssz_bytes_len<E: EthSpec>(state: &BeaconState<E>) -> usize {
-            state
-                .ssz_bytes_len()
-                .checked_add(1)
-                .expect("encoded length must be less than usize::max")
-        }
-
-        pub fn ssz_append<E: EthSpec>(state: &BeaconState<E>, buf: &mut Vec<u8>) {
-            let fork_name = state.fork_name_unchecked();
-            fork_name.ssz_append(buf);
-            state.ssz_append(buf);
-        }
-
-        pub fn as_ssz_bytes<E: EthSpec>(state: &BeaconState<E>) -> Vec<u8> {
-            let mut buf = vec![];
-            ssz_append(state, &mut buf);
-
-            buf
-        }
-    }
-
-    pub mod decode {
-        use super::*;
-        #[allow(unused_imports)]
-        use ssz::*;
-
-        pub fn is_ssz_fixed_len() -> bool {
-            false
-        }
-
-        pub fn ssz_fixed_len() -> usize {
-            BYTES_PER_LENGTH_OFFSET
-        }
-
-        pub fn from_ssz_bytes<E: EthSpec>(bytes: &[u8]) -> Result<BeaconState<E>, DecodeError> {
-            let fork_byte = bytes
-                .first()
-                .copied()
-                .ok_or(DecodeError::OutOfBoundsByte { i: 0 })?;
-            let body = bytes
-                .get(1..)
-                .ok_or(DecodeError::OutOfBoundsByte { i: 1 })?;
-            match ForkName::from_ssz_bytes(&[fork_byte])? {
-                ForkName::Base => Ok(BeaconState::Base(BeaconStateBase::from_ssz_bytes(body)?)),
-                ForkName::Altair => Ok(BeaconState::Altair(BeaconStateAltair::from_ssz_bytes(
-                    body,
-                )?)),
-                ForkName::Merge => Ok(BeaconState::Merge(BeaconStateMerge::from_ssz_bytes(body)?)),
-                ForkName::Capella => Ok(BeaconState::Capella(BeaconStateCapella::from_ssz_bytes(
-                    body,
-                )?)),
-                ForkName::Deneb => Ok(BeaconState::Deneb(BeaconStateDeneb::from_ssz_bytes(body)?)),
-            }
-        }
-    }
-}
```
