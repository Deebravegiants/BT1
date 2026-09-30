# [?] Fix custody context initialization race condition that caused panic (#8391)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-11-17
Source: https://github.com/sigp/lighthouse/commit/af1d9b99911e2467a56ce9f308f06ec7a9ead3eb
Type: security-commit

## Details
Fix custody context initialization race condition that caused panic (#8391)

Take 2 of #8390.

Fixes the race condition properly instead of propagating the error. I think this is a better alternative, and doesn't seem to look that bad.


  * Lift node id loading or generation from `NetworkService ` startup to the `ClientBuilder`, so that it can be used to compute custody columns for the beacon chain without waiting for Network bootstrap.

I've considered and implemented a few alternatives:
1. passing `node_id` to beacon chain builder and compute columns when creating `CustodyContext`. This approach isn't good for separation of concerns and isn't great for testability
2. passing `ordered_custody_groups` to beacon chain. `CustodyContext` only uses this to compute ordered custody columns, so we might as well lift this logic out, so we don't have to do error handling in `CustodyContext` construction. Less tests to update;.


Co-Authored-By: Jimmy Chen <jchen.tc@gmail.com>

## Patch
### beacon_node/beacon_chain/src/builder.rs
```diff
@@ -40,9 +40,10 @@ use std::time::Duration;
 use store::{Error as StoreError, HotColdDB, ItemStore, KeyValueStoreOp};
 use task_executor::{ShutdownReason, TaskExecutor};
 use tracing::{debug, error, info};
+use types::data_column_custody_group::CustodyIndex;
 use types::{
-    BeaconBlock, BeaconState, BlobSidecarList, ChainSpec, DataColumnSidecarList, Epoch, EthSpec,
-    FixedBytesExtended, Hash256, Signature, SignedBeaconBlock, Slot,
+    BeaconBlock, BeaconState, BlobSidecarList, ChainSpec, ColumnIndex, DataColumnSidecarList,
+    Epoch, EthSpec, FixedBytesExtended, Hash256, Signature, SignedBeaconBlock, Slot,
 };
 
 /// An empty struct used to "witness" all the `BeaconChainTypes` traits. It has no user-facing
@@ -102,6 +103,7 @@ pub struct BeaconChainBuilder<T: BeaconChainTypes> {
     task_executor: Option<TaskExecutor>,
     validator_monitor_config: Option<ValidatorMonitorConfig>,
     node_custody_type: NodeCustodyType,
+    ordered_custody_column_indices: Option<Vec<CustodyIndex>>,
     rng: Option<Box<dyn RngCore + Send>>,
 }
 
@@ -141,6 +143,7 @@ where
             task_executor: None,
             validator_monitor_config: None,
             node_custody_type: NodeCustodyType::Fullnode,
+            ordered_custody_column_indices: None,
             rng: None,
         }
     }
@@ -647,6 +650,16 @@ where
         self
     }
 
+    /// Sets the ordered custody column indices for this node.
+    /// This is used to determine the data columns the node is required to custody.
+    pub fn ordered_custody_column_indices(
+        mut self,
+        ordered_custody_column_indices: Vec<ColumnIndex>,
+    ) -> Self {
+        self.ordered_custody_column_indices = Some(ordered_custody_column_indices);
+        self
+    }
+
     /// Sets the `BeaconChain` event handler backend.
     ///
     /// For example, provide `ServerSentEventHandler` as a `handler`.
@@ -740,6 +753,9 @@ where
             .genesis_state_root
             .ok_or("Cannot build without a genesis state root")?;
         let validator_monitor_config = self.validator_monitor_config.unwrap_or_default();
+        let ordered_custody_column_indices = self
+            .ordered_custody_column_indices
+            .ok_or("Cannot build without ordered custody column indices")?;
         let rng = self.rng.ok_or("Cannot build without an RNG")?;
         let beacon_proposer_cache: Arc<Mutex<BeaconProposerCache>> = <_>::default();
 
@@ -942,11 +958,16 @@ where
                 custody,
                 self.node_custody_type,
                 head_epoch,
+                ordered_custody_column_indices,
                 &self.spec,
             )
         } else {
             (
-                CustodyContext::new(self.node_custody_type, &self.spec),
+                CustodyContext::new(
+                    self.node_custody_type,
+                    ordered_custody_column_indices,
+                    &self.spec,
+                ),
                 None,
             )
         };
@@ -1220,7 +1241,9 @@ fn build_data_columns_from_blobs<E: EthSpec>(
 #[cfg(test)]
 mod test {
     use super::*;
-    use crate::test_utils::{EphemeralHarnessType, get_kzg};
+    use crate::test_utils::{
+        EphemeralHarnessType, generate_data_column_indices_rand_order, get_kzg,
+    };
     use ethereum_hashing::hash;
     use genesis::{
         DEFAULT_ETH1_BLOCK_HASH, generate_deterministic_keypairs, interop_genesis_state,
@@ -1272,6 +1295,9 @@ mod test {
             .expect("should configure testing slot clock")
             .shutdown_sender(shutdown_tx)
             .rng(Box::new(StdRng::seed_from_u64(42)))
+            .ordered_custody_column_indices(
+                generate_data_column_indices_rand_order::<MinimalEthSpec>(),
+            )
             .build()
             .expect("should build");
 
```

### beacon_node/beacon_chain/src/custody_context.rs
```diff
@@ -2,13 +2,11 @@ use parking_lot::RwLock;
 use serde::{Deserialize, Serialize};
 use ssz_derive::{Decode, Encode};
 use std::marker::PhantomData;
-use std::sync::OnceLock;
 use std::{
     collections::{BTreeMap, HashMap},
     sync::atomic::{AtomicU64, Ordering},
 };
 use tracing::{debug, warn};
-use types::data_column_custody_group::{CustodyIndex, compute_columns_for_custody_group};
 use types::{ChainSpec, ColumnIndex, Epoch, EthSpec, Slot};
 
 /// A delay before making the CGC change effective to the data availability checker.
@@ -206,7 +204,7 @@ fn get_validators_custody_requirement(validator_custody_units: u64, spec: &Chain
 /// Therefore, the custody count at any point in time is calculated as the max of
 /// the validator custody at that time and the current cli params.
 ///
-/// Choosing the max ensures that we always have the minimum required columns and
+/// Choosing the max ensures that we always have the minimum required columns, and
 /// we can adjust the `status.earliest_available_slot` value to indicate to our peers
 /// the columns that we can guarantee to serve.
 #[derive(Debug, Copy, Clone, PartialEq, Eq, Default, Deserialize, Serialize)]
@@ -218,7 +216,7 @@ pub enum NodeCustodyType {
     /// wants to subscribe to the minimum number of columns to enable
     /// reconstruction (50%) of the full blob data on demand.
     SemiSupernode,
-    /// The node isn't running with with any explicit cli parameters
+    /// The node isn't running with any explicit cli parameters
     /// or is running with cli parameters to indicate that it wants
     /// to only subscribe to the minimal custody requirements.
     #[default]
@@ -248,9 +246,9 @@ pub struct CustodyContext<E: EthSpec> {
     validator_custody_count: AtomicU64,
     /// Maintains all the validators that this node is connected to currently
     validator_registrations: RwLock<ValidatorRegistrations>,
-    /// Stores an immutable, ordered list of all custody columns as determined by the node's NodeID
-    /// on startup.
-    all_custody_columns_ordered: OnceLock<Box<[ColumnIndex]>>,
+    /// Stores an immutable, ordered list of all data column indices as determined by the node's NodeID
+    /// on startup. This used to determine the node's custody columns.
+    ordered_custody_column_indices: Vec<ColumnIndex>,
     _phantom_data: PhantomData<E>,
 }
 
@@ -259,15 +257,19 @@ impl<E: EthSpec> CustodyContext<E> {
     /// exists.
     ///
     /// The `node_custody_type` value is based on current cli parameters.
-    pub fn new(node_custody_type: NodeCustodyType, spec: &ChainSpec) -> Self {
+    pub fn new(
+        node_custody_type: NodeCustodyType,
+        ordered_custody_column_indices: Vec<ColumnIndex>,
+        spec: &ChainSpec,
+    ) -> Self {
         let cgc_override = node_custody_type.get_custody_count_override(spec);
         // If there's no override, we initialise `validator_custody_count` to 0. This has been the
         // existing behaviour and we maintain this for now to avoid a semantic schema change until
         // a later release.
         Self {
             validator_custody_count: AtomicU64::new(cgc_override.unwrap_or(0)),
             validator_registrations: RwLock::new(ValidatorRegistrations::new(cgc_override)),
-            all_custody_columns_ordered: OnceLock::new(),
+            ordered_custody_column_indices,
             _phantom_data: PhantomData,
         }
     }
@@ -290,6 +292,7 @@ impl<E: EthSpec> CustodyContext<E> {
         ssz_context: CustodyContextSsz,
         node_custody_type: NodeCustodyType,
         head_epoch: Epoch,
+        ordered_custody_column_indices: Vec<ColumnIndex>,
         spec: &ChainSpec,
     ) -> (Self, Option<CustodyCountChanged>) {
         let CustodyContextSsz {
@@ -355,39 +358,13 @@ impl<E: EthSpec> CustodyContext<E> {
                     .into_iter()
                     .collect(),
             }),
-            all_custody_columns_ordered: OnceLock::new(),
+            ordered_custody_column_indices,
             _phantom_data: PhantomData,
         };
 
         (custody_context, custody_count_changed)
     }
 
-    /// Initializes an ordered list of data columns based on provided custody groups.
-    ///
-    /// # Arguments
-    /// * `all_custody_groups_ordered` - Vector of custody group indices to map to columns
-    /// * `spec` - Chain specification containing custody parameters
-    ///
-    /// # Returns
-    /// Ok(()) if initialization succeeds, Err with description string if it fails
-    pub fn init_ordered_data_columns_from_custody_groups(
-        &self,
-        all_custody_groups_ordered: Vec<CustodyIndex>,
-        spec: &ChainSpec,
-    ) -> Result<(), String> {
-        let mut ordered_custody_columns = vec![];
-        for custody_index in all_custody_groups_ordered {
-            let columns = compute_columns_for_custody_group::<E>(custody_index, spec)
-                .map_err(|e| format!("Failed to compute columns for custody group {e:?}"))?;
-            ordered_custody_columns.extend(columns);
-        }
-        self.all_custody_columns_ordered
-            .set(ordered_custody_columns.into_boxed_slice())
-            .map_err(|_| {
-                "Failed to initialise CustodyContext with computed custody columns".to_string()
-            })
-    }
-
     /// Register a new validator index and updates the list of validators if required.
     ///
     /// Also modifies the internal structures if the validator custody has changed to
@@ -497,11 +474,7 @@ impl<E: EthSpec> CustodyContext<E> {
     /// A slice of ordered column indices that should be sampled for this epoch based on the node's custody configuration
     pub fn sampling_columns_for_epoch(&self, epoch: Epoch, spec: &ChainSpec) -> &[ColumnIndex] {
         let num_of_columns_to_sample = self.num_of_data_columns_to_sample(epoch, spec);
-        let all_columns_ordered = self
-            .all_custody_columns_ordered
-            .get()
-            .expect("all_custody_columns_ordered should be initialized");
-        &all_columns_ordered[..num_of_columns_to_sample]
+        &self.ordered_custody_column_indices[..num_of_columns_to_sample]
     }
 
     /// Returns the ordered list of column indices that the node is assigned to custody
@@ -528,12 +501,11 @@ impl<E: EthSpec> CustodyContext<E> {
             self.custody_group_count_at_head(spec) as usize
         };
 
-        let all_columns_ordered = self
-            .all_custody_columns_ordered
-            .get()
-            .expect("all_custody_columns_ordered should be initialized");
+        // This is an unnecessary conversion for spec compliance, basically just multiplying by 1.
+        let columns_per_custody_group = spec.data_columns_per_group::<E>() as usize;
+        let custody_column_count = columns_per_custody_group * custody_group_count;
 
-        &all_columns_ordered[..custody_group_count]
+        &self.ordered_custody_column_indices[..custody_column_count]
     }
 
     /// The node has completed backfill for this epoch. Update the internal records so the function
@@ -599,11 +571,9 @@ impl<E: EthSpec> From<&CustodyContext<E>> for CustodyContextSsz {
 
 #[cfg(test)]
 mod tests {
-    use rand::rng;
-    use rand::seq::SliceRandom;
-    use types::MainnetEthSpec;
-
     use super::*;
+    use crate::test_utils::generate_data_column_indices_rand_order;
+    use types::MainnetEthSpec;
 
     type E = MainnetEthSpec;
 
@@ -623,13 +593,10 @@ mod tests {
             ssz_context,
             NodeCustodyType::Fullnode,
             head_epoch,
+            generate_data_column_indices_rand_order::<E>(),
             spec,
         );
 
-        let all_custody_groups_ordered = (0..spec.number_of_custody_groups).collect::<Vec<_>>();
-        custody_context
-            .init_ordered_data_columns_from_custody_groups(all_custody_groups_ordered, spec)
-            .expect("should initialise ordered data columns");
         custody_context
     }
 
@@ -668,6 +635,7 @@ mod tests {
                 ssz_context,
                 target_node_custody_type,
                 head_epoch,
+                generate_data_column_indices_rand_order::<E>(),
                 spec,
             );
 
@@ -738,6 +706,7 @@ mod tests {
                 ssz_context,
                 target_node_custody_type,
                 head_epoch,
+                generate_data_column_indices_rand_order::<E>(),
                 spec,
             );
 
@@ -759,7 +728,11 @@ mod tests {
     #[test]
     fn no_validators_supernode_default() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Supernode, &spec);
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Supernode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        );
         assert_eq!(
             custody_context.custody_group_count_at_head(&spec),
             spec.number_of_custody_groups
@@ -773,7 +746,11 @@ mod tests {
     #[test]
     fn no_validators_semi_supernode_default() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::SemiSupernode, &spec);
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::SemiSupernode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        );
         assert_eq!(
             custody_context.custody_group_count_at_head(&spec),
             spec.number_of_custody_groups / 2
@@ -787,7 +764,11 @@ mod tests {
     #[test]
     fn no_validators_fullnode_default() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Fullnode, &spec);
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Fullnode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        );
         assert_eq!(
             custody_context.custody_group_count_at_head(&spec),
             spec.custody_requirement,
@@ -802,7 +783,11 @@ mod tests {
     #[test]
     fn register_single_validator_should_update_cgc() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Fullnode, &spec);
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Fullnode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        );
         let bal_per_additional_group = spec.balance_per_additional_custody_group;
         let min_val_custody_requirement = spec.validator_custody_requirement;
         // One single node increases its balance over 3 epochs.
@@ -826,7 +811,11 @@ mod tests {
     #[test]
     fn register_multiple_validators_should_update_cgc() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Fullnode, &spec);
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Fullnode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        );
         let bal_per_additional_group = spec.balance_per_additional_custody_group;
         let min_val_custody_requirement = spec.validator_custody_requirement;
         // Add 3 validators over 3 epochs.
@@ -863,7 +852,11 @@ mod tests {
     #[test]
     fn register_validators_should_not_update_cgc_for_supernode() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Supernode, &spec);
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Supernode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        );
         let bal_per_additional_group = spec.balance_per_additional_custody_group;
 
         // Add 3 validators over 3 epochs.
@@ -901,7 +894,11 @@ mod tests {
     #[test]
     fn cgc_change_should_be_effective_to_sampling_after_delay() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Fullnode, &spec);
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Fullnode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        );
         let current_slot = Slot::new(10);
         let current_epoch = current_slot.epoch(E::slots_per_epoch());
         let default_sampling_size =
@@ -932,7 +929,11 @@ mod tests {
     #[test]
     fn validator_dropped_after_no_registrations_within_expiry_should_not_reduce_cgc() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Fullnode, &spec);
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Fullnode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        );
         let current_slot = Slot::new(10);
         let val_custody_units_1 = 10;
         let val_custody_units_2 = 5;
@@ -974,7 +975,11 @@ mod tests {
     #[test]
     fn validator_dropped_after_no_registrations_within_expiry() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Fullnode, &spec);
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Fullnode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        );
         let current_slot = Slot::new(10);
         let val_custody_units_1 = 10;
         let val_custody_units_2 = 5;
@@ -1021,37 +1026,6 @@ mod tests {
         );
     }
 
-    #[test]
-    fn should_init_ordered_data_columns_and_return_sampling_columns() {
-        let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Fullnode, &spec);
-        let sampling_size = custody_context.num_of_data_columns_to_sample(Epoch::new(0), &spec);
-
-        // initialise ordered columns
-        let mut all_custody_groups_ordered = (0..spec.number_of_custody_groups).collect::<Vec<_>>();
-        all_custody_groups_ordered.shuffle(&mut rng());
-
-        custody_context
-            .init_ordered_data_columns_from_custody_groups(
-                all_custody_groups_ordered.clone(),
-                &spec,
-            )
-            .expect("should initialise ordered data columns");
-
-        let actual_sampling_columns =
-            custody_context.sampling_columns_for_epoch(Epoch::new(0), &spec);
-
-        let expected_sampling_columns = &all_custody_groups_ordered
-            .iter()
-            .flat_map(|custody_index| {
-                compute_columns_for_custody_group::<E>(*custody_index, &spec)
-                    .expect("should compute columns for custody group")
-            })
-            .collect::<Vec<_>>()[0..sampling_size];
-
-        assert_eq!(actual_sampling_columns, expected_sampling_columns)
-    }
-
     /// Update the validator every epoch and assert cgc against expected values.
     fn register_validators_and_assert_cgc<E: EthSpec>(
         custody_context: &CustodyContext<E>,
@@ -1077,12 +1051,12 @@ mod tests {
     #[test]
     fn custody_columns_for_epoch_no_validators_fullnode() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Fullnode, &spec);
-        let all_custody_groups_ordered = (0..spec.number_of_custody_groups).collect::<Vec<_>>();
-
-        custody_context
-            .init_ordered_data_columns_from_custody_groups(all_custody_groups_ordered, &spec)
-            .expect("should initialise ordered data columns");
+        let ordered_custody_column_indices = generate_data_column_indices_rand_order::<E>();
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Fullnode,
+            ordered_custody_column_indices,
+            &spec,
+        );
 
         assert_eq!(
             custody_context.custody_columns_for_epoch(None, &spec).len(),
@@ -1093,12 +1067,12 @@ mod tests {
     #[test]
     fn custody_columns_for_epoch_no_validators_supernode() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Supernode, &spec);
-        let all_custody_groups_ordered = (0..spec.number_of_custody_groups).collect::<Vec<_>>();
-
-        custody_context
-            .init_ordered_data_columns_from_custody_groups(all_custody_groups_ordered, &spec)
-            .expect("should initialise ordered data columns");
+        let ordered_custody_column_indices = generate_data_column_indices_rand_order::<E>();
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Supernode,
+            ordered_custody_column_indices,
+            &spec,
+        );
 
         assert_eq!(
             custody_context.custody_columns_for_epoch(None, &spec).len(),
@@ -1109,14 +1083,14 @@ mod tests {
     #[test]
     fn custody_columns_for_epoch_with_validators_should_match_cgc() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Fullnode, &spec);
-        let all_custody_groups_ordered = (0..spec.number_of_custody_groups).collect::<Vec<_>>();
+        let ordered_custody_column_indices = generate_data_column_indices_rand_order::<E>();
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Fullnode,
+            ordered_custody_column_indices,
+            &spec,
+        );
         let val_custody_units = 10;
 
-        custody_context
-            .init_ordered_data_columns_from_custody_groups(all_custody_groups_ordered, &spec)
-            .expect("should initialise ordered data columns");
-
         let _ = custody_context.register_validators(
             vec![(
                 0,
@@ -1135,14 +1109,14 @@ mod tests {
     #[test]
     fn custody_columns_for_epoch_specific_epoch_uses_epoch_cgc() {
         let spec = E::default_spec();
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::Fullnode, &spec);
-        let all_custody_groups_ordered = (0..spec.number_of_custody_groups).collect::<Vec<_>>();
+        let ordered_custody_column_indices = generate_data_column_indices_rand_order::<E>();
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::Fullnode,
+            ordered_custody_column_indices,
+            &spec,
+        );
         let test_epoch = Epoch::new(5);
 
-        custody_context
-            .init_ordered_data_columns_from_custody_groups(all_custody_groups_ordered, &spec)
-            .expect("should initialise ordered data columns");
-
         let expected_cgc = custody_context.custody_group_count_at_epoch(test_epoch, &spec);
         assert_eq!(
             custody_context
@@ -1165,6 +1139,7 @@ mod tests {
             ssz_context,
             NodeCustodyType::Fullnode,
             Epoch::new(0),
+            generate_data_column_indices_rand_order::<E>(),
             &spec,
         );
 
@@ -1198,7 +1173,11 @@ mod tests {
     fn restore_semi_supernode_with_validators_can_exceed_64() {
         let spec = E::default_spec();
         let semi_supernode_cgc = spec.number_of_custody_groups / 2; // 64
-        let custody_context = CustodyContext::<E>::new(NodeCustodyType::SemiSupernode, &spec);
+        let custody_context = CustodyContext::<E>::new(
+            NodeCustodyType::SemiSupernode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        );
 
         // Verify initial CGC is 64 (semi-supernode)
         assert_eq!(
@@ -1348,6 +1327,7 @@ mod tests {
             ssz_context,
             NodeCustodyType::Fullnode,
             Epoch::new(20),
+            generate_data_column_indices_rand_order::<E>(),
             &spec,
         );
 
```

### beacon_node/beacon_chain/src/data_availability_checker.rs
```diff
@@ -866,11 +866,11 @@ mod test {
     use crate::CustodyContext;
     use crate::custody_context::NodeCustodyType;
     use crate::test_utils::{
-        EphemeralHarnessType, NumBlobs, generate_rand_block_and_data_columns, get_kzg,
+        EphemeralHarnessType, NumBlobs, generate_data_column_indices_rand_order,
+        generate_rand_block_and_data_columns, get_kzg,
     };
     use rand::SeedableRng;
     use rand::prelude::StdRng;
-    use rand::seq::SliceRandom;
     use slot_clock::{SlotClock, TestingSlotClock};
     use std::collections::HashSet;
     use std::sync::Arc;
@@ -892,8 +892,6 @@ mod test {
 
         let da_checker = new_da_checker(spec.clone());
         let custody_context = &da_checker.custody_context;
-        let all_column_indices_ordered =
-            init_custody_context_with_ordered_columns(custody_context, &mut rng, &spec);
 
         // GIVEN a single 32 ETH validator is attached slot 0
         let epoch = Epoch::new(0);
@@ -926,7 +924,8 @@ mod test {
             &spec,
         );
         let block_root = Hash256::random();
-        let requested_columns = &all_column_indices_ordered[..10];
+        let custody_columns = custody_context.custody_columns_for_epoch(None, &spec);
+        let requested_columns = &custody_columns[..10];
         da_checker
             .put_rpc_custody_columns(
                 block_root,
@@ -971,8 +970,6 @@ mod test {
 
         let da_checker = new_da_checker(spec.clone());
         let custody_context = &da_checker.custody_context;
-        let all_column_indices_ordered =
-            init_custody_context_with_ordered_columns(custody_context, &mut rng, &spec);
 
         // GIVEN a single 32 ETH validator is attached slot 0
         let epoch = Epoch::new(0);
@@ -1006,7 +1003,8 @@ mod test {
             &spec,
         );
         let block_root = Hash256::random();
-        let requested_columns = &all_column_indices_ordered[..10];
+        let custody_columns = custody_context.custody_columns_for_epoch(None, &spec);
+        let requested_columns = &custody_columns[..10];
         let gossip_columns = data_columns
             .into_iter()
             .filter(|d| requested_columns.contains(&d.index))
@@ -1096,8 +1094,6 @@ mod test {
 
         let da_checker = new_da_checker(spec.clone());
         let custody_context = &da_checker.custody_context;
-        let all_column_indices_ordered =
-            init_custody_context_with_ordered_columns(custody_context, &mut rng, &spec);
 
         // Set custody requirement to 65 columns (enough to trigger reconstruction)
         let epoch = Epoch::new(1);
@@ -1127,7 +1123,8 @@ mod test {
 
         // Add 64 columns to the da checker (enough to be able to reconstruct)
         // Order by all_column_indices_ordered, then take first 64
-        let custody_columns = all_column_indices_ordered
+        let custody_columns = custody_context.custody_columns_for_epoch(None, &spec);
+        let custody_columns = custody_columns
             .iter()
             .filter_map(|&col_idx| data_columns.iter().find(|d| d.index == col_idx).cloned())
             .take(64)
@@ -1177,19 +1174,6 @@ mod test {
         );
     }
 
-    fn init_custody_context_with_ordered_columns(
-        custody_context: &Arc<CustodyContext<E>>,
-        mut rng: &mut StdRng,
-        spec: &ChainSpec,
-    ) -> Vec<u64> {
-        let mut all_data_columns = (0..spec.number_of_custody_groups).collect::<Vec<_>>();
-        all_data_columns.shuffle(&mut rng);
-        custody_context
-            .init_ordered_data_columns_from_custody_groups(all_data_columns.clone(), spec)
-            .expect("should initialise ordered custody columns");
-        all_data_columns
-    }
-
     fn new_da_checker(spec: Arc<ChainSpec>) -> DataAvailabilityChecker<T> {
         let slot_clock = TestingSlotClock::new(
             Slot::new(0),
@@ -1198,7 +1182,12 @@ mod test {
         );
         let kzg = get_kzg(&spec);
         let store = Arc::new(HotColdDB::open_ephemeral(<_>::default(), spec.clone()).unwrap());
-        let custody_context = Arc::new(CustodyContext::new(NodeCustodyType::Fullnode, &spec));
+        let ordered_custody_column_indices = generate_data_column_indices_rand_order::<E>();
+        let custody_context = Arc::new(CustodyContext::new(
+            NodeCustodyType::Fullnode,
+            ordered_custody_column_indices,
+            &spec,
+        ));
         let complete_blob_backfill = false;
         DataAvailabilityChecker::new(
             complete_blob_backfill,
```

### beacon_node/beacon_chain/src/data_availability_checker/overflow_lru_cache.rs
```diff
@@ -823,6 +823,7 @@ impl<T: BeaconChainTypes> DataAvailabilityCheckerInner<T> {
 mod test {
     use super::*;
 
+    use crate::test_utils::generate_data_column_indices_rand_order;
     use crate::{
         blob_verification::GossipVerifiedBlob,
         block_verification::PayloadVerificationOutcome,
@@ -1023,7 +1024,11 @@ mod test {
         let spec = harness.spec.clone();
         let test_store = harness.chain.store.clone();
         let capacity_non_zero = new_non_zero_usize(capacity);
-        let custody_context = Arc::new(CustodyContext::new(NodeCustodyType::Fullnode, &spec));
+        let custody_context = Arc::new(CustodyContext::new(
+            NodeCustodyType::Fullnode,
+            generate_data_column_indices_rand_order::<E>(),
+            &spec,
+        ));
         let cache = Arc::new(
             DataAvailabilityCheckerInner::<T>::new(
                 capacity_non_zero,
```

### beacon_node/beacon_chain/src/test_utils.rs
```diff
@@ -42,6 +42,7 @@ use parking_lot::{Mutex, RwLockWriteGuard};
 use rand::Rng;
 use rand::SeedableRng;
 use rand::rngs::StdRng;
+use rand::seq::SliceRandom;
 use rayon::prelude::*;
 use sensitive_url::SensitiveUrl;
 use slot_clock::{SlotClock, TestingSlotClock};
@@ -59,6 +60,7 @@ use store::{HotColdDB, ItemStore, MemoryStore, config::StoreConfig};
 use task_executor::TaskExecutor;
 use task_executor::{ShutdownReason, test_utils::TestRuntime};
 use tree_hash::TreeHash;
+use types::data_column_custody_group::CustodyIndex;
 use types::indexed_attestation::IndexedAttestationBase;
 use types::payload::BlockProductionVersion;
 use types::test_utils::TestRandom;
@@ -567,6 +569,7 @@ where
             .shutdown_sender(shutdown_tx)
             .chain_config(chain_config)
             .node_custody_type(self.node_custody_type)
+            .ordered_custody_column_indices(generate_data_column_indices_rand_order::<E>())
             .event_handler(Some(ServerSentEventHandler::new_with_capacity(5)))
             .validator_monitor_config(validator_monitor_config)
             .rng(Box::new(StdRng::seed_from_u64(42)));
@@ -596,15 +599,6 @@ where
 
         let chain = builder.build().expect("should build");
 
-        chain
-            .data_availability_checker
-            .custody_context()
-            .init_ordered_data_columns_from_custody_groups(
-                (0..spec.number_of_custody_groups).collect(),
-                &spec,
-            )
-            .expect("should initialise custody context");
-
         BeaconChainHarness {
             spec: chain.spec.clone(),
             chain: Arc::new(chain),
@@ -3431,3 +3425,9 @@ pub fn generate_data_column_sidecars_from_block<E: EthSpec>(
     )
     .unwrap()
 }
+
+pub fn generate_data_column_indices_rand_order<E: EthSpec>() -> Vec<CustodyIndex> {
+    let mut indices = (0..E::number_of_columns() as u64).collect::<Vec<_>>();
+    indices.shuffle(&mut StdRng::seed_from_u64(42));
+    indices
+}
```

### beacon_node/beacon_chain/tests/store_tests.rs
```diff
@@ -7,11 +7,11 @@ use beacon_chain::custody_context::CUSTODY_CHANGE_DA_EFFECTIVE_DELAY_SECONDS;
 use beacon_chain::data_availability_checker::AvailableBlock;
 use beacon_chain::historical_data_columns::HistoricalDataColumnError;
 use beacon_chain::schema_change::migrate_schema;
-use beacon_chain::test_utils::SyncCommitteeStrategy;
 use beacon_chain::test_utils::{
     AttestationStrategy, BeaconChainHarness, BlockStrategy, DiskHarnessType, get_kzg,
     mock_execution_layer_from_parts, test_spec,
 };
+use beacon_chain::test_utils::{SyncCommitteeStrategy, generate_data_column_indices_rand_order};
 use beacon_chain::{
     BeaconChain, BeaconChainError, BeaconChainTypes, BeaconSnapshot, BlockError, ChainConfig,
     NotifyExecutionLayer, ServerSentEventHandler, WhenSlotSkipped,
@@ -2881,17 +2881,10 @@ async fn weak_subjectivity_sync_test(
         .shutdown_sender(shutdown_tx)
         .event_handler(Some(ServerSentEventHandler::new_with_capacity(1)))
         .execution_layer(Some(mock.el))
+        .ordered_custody_column_indices(generate_data_column_indices_rand_order::<E>())
         .rng(Box::new(StdRng::seed_from_u64(42)))
         .build()
         .expect("should build");
-    beacon_chain
-        .data_availability_checker
-        .custody_context()
-        .init_ordered_data_columns_from_custody_groups(
-            (0..spec.number_of_custody_groups).collect(),
-            &spec,
-        )
-        .unwrap();
 
     let beacon_chain = Arc::new(beacon_chain);
     let wss_block_root = wss_block.canonical_root();
```

### beacon_node/client/src/builder.rs
```diff
@@ -28,6 +28,7 @@ use execution_layer::ExecutionLayer;
 use execution_layer::test_utils::generate_genesis_header;
 use futures::channel::mpsc::Receiver;
 use genesis::{DEFAULT_ETH1_BLOCK_HASH, interop_genesis_state};
+use lighthouse_network::identity::Keypair;
 use lighthouse_network::{NetworkGlobals, prometheus_client::registry::Registry};
 use monitoring_api::{MonitoringHttpClient, ProcessType};
 use network::{NetworkConfig, NetworkSenders, NetworkService};
@@ -42,7 +43,7 @@ use std::time::{SystemTime, UNIX_EPOCH};
 use store::database::interface::BeaconNodeBackend;
 use timer::spawn_timer;
 use tracing::{debug, info, warn};
-use types::data_column_custody_group::get_custody_groups_ordered;
+use types::data_column_custody_group::compute_ordered_custody_column_indices;
 use types::{
     BeaconState, BlobSidecarList, ChainSpec, EthSpec, ExecutionBlockHash, Hash256,
     SignedBeaconBlock, test_utils::generate_deterministic_keypairs,
@@ -154,6 +155,7 @@ where
         mut self,
         client_genesis: ClientGenesis,
         config: ClientConfig,
+        node_id: [u8; 32],
     ) -> Result<Self, String> {
         let store = self.store.clone();
         let chain_spec = self.chain_spec.clone();
@@ -191,6 +193,11 @@ where
             Kzg::new_from_trusted_setup_no_precomp(&config.trusted_setup).map_err(kzg_err_msg)?
         };
 
+        let ordered_custody_column_indices =
+            compute_ordered_custody_column_indices::<E>(node_id, &spec).map_err(|e| {
+                format!("Failed to compute ordered custody column indices: {:?}", e)
+            })?;
+
         let builder = BeaconChainBuilder::new(eth_spec_instance, Arc::new(kzg))
             .store(store)
             .task_executor(context.executor.clone())
@@ -203,6 +210,7 @@ where
             .event_handler(event_handler)
             .execution_layer(execution_layer)
             .node_custody_type(config.chain.node_custody_type)
+            .ordered_custody_column_indices(ordered_custody_column_indices)
             .validator_monitor_config(config.validator_monitor.clone())
             .rng(Box::new(
                 StdRng::try_from_rng(&mut OsRng)
@@ -463,7 +471,11 @@ where
     }
 
     /// Starts the networking stack.
-    pub async fn network(mut self, config: Arc<NetworkConfig>) -> Result<Self, String> {
+    pub async fn network(
+        mut self,
+        config: Arc<NetworkConfig>,
+        local_keypair: Keypair,
+    ) -> Result<Self, String> {
         let beacon_chain = self
             .beacon_chain
             .clone()
@@ -491,12 +503,11 @@ where
             context.executor,
             libp2p_registry.as_mut(),
             beacon_processor_channels.beacon_processor_tx.clone(),
+            local_keypair,
         )
         .await
         .map_err(|e| format!("Failed to start network: {:?}", e))?;
 
-        init_custody_context(beacon_chain, &network_globals)?;
-
         self.network_globals = Some(network_globals);
         self.network_senders = Some(network_senders);
         self.libp2p_registry = libp2p_registry;
@@ -798,21 +809,6 @@ where
     }
 }
 
-fn init_custody_context<T: BeaconChainTypes>(
-    chain: Arc<BeaconChain<T>>,
-    network_globals: &NetworkGlobals<T::EthSpec>,
-) -> Result<(), String> {
-    let node_id = network_globals.local_enr().node_id().raw();
-    let spec = &chain.spec;
-    let custody_groups_ordered =
-        get_custody_groups_ordered(node_id, spec.number_of_custody_groups, spec)
-            .map_err(|e| format!("Failed to compute custody groups: {:?}", e))?;
-    chain
-        .data_availability_checker
-        .custody_context()
-        .init_ordered_data_columns_from_custody_groups(custody_groups_ordered, spec)
-}
-
 impl<TSlotClock, E, THotStore, TColdStore>
     ClientBuilder<Witness<TSlotClock, E, THotStore, TColdStore>>
 where
```

### beacon_node/lighthouse_network/src/lib.rs
```diff
@@ -109,7 +109,7 @@ pub use discovery::Eth2Enr;
 pub use discv5;
 pub use gossipsub::{IdentTopic, MessageAcceptance, MessageId, Topic, TopicHash};
 pub use libp2p;
-pub use libp2p::{Multiaddr, multiaddr};
+pub use libp2p::{Multiaddr, identity, multiaddr};
 pub use libp2p::{PeerId, Swarm, core::ConnectedPoint};
 pub use peer_manager::{
     ConnectionDirection, PeerConnectionStatus, PeerInfo, PeerManager, SyncInfo, SyncStatus,
```

### beacon_node/lighthouse_network/src/service/mod.rs
```diff
@@ -26,6 +26,7 @@ use gossipsub::{
     TopicScoreParams,
 };
 use gossipsub_scoring_parameters::{PeerScoreSettings, lighthouse_gossip_thresholds};
+use libp2p::identity::Keypair;
 use libp2p::multiaddr::{self, Multiaddr, Protocol as MProtocol};
 use libp2p::swarm::behaviour::toggle::Toggle;
 use libp2p::swarm::{NetworkBehaviour, Swarm, SwarmEvent};
@@ -171,11 +172,10 @@ impl<E: EthSpec> Network<E> {
         executor: task_executor::TaskExecutor,
         mut ctx: ServiceContext<'_>,
         custody_group_count: u64,
+        local_keypair: Keypair,
     ) -> Result<(Self, Arc<NetworkGlobals<E>>), String> {
         let config = ctx.config.clone();
         trace!("Libp2p Service starting");
-        // initialise the node's ID
-        let local_keypair = utils::load_private_key(&config);
 
         // Trusted peers will also be marked as explicit in GossipSub.
         // Cfr. https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md#explicit-peering-agreements
```

### beacon_node/lighthouse_network/tests/common.rs
```diff
@@ -16,6 +16,7 @@ use types::{
 
 type E = MinimalEthSpec;
 
+use lighthouse_network::identity::secp256k1;
 use lighthouse_network::rpc::config::InboundRateLimiterConfig;
 use tempfile::Builder as TempBuilder;
 
@@ -138,10 +139,15 @@ pub async fn build_libp2p_instance(
         libp2p_registry: None,
     };
     Libp2pInstance(
-        LibP2PService::new(executor, libp2p_context, custody_group_count)
-            .await
-            .expect("should build libp2p instance")
-            .0,
+        LibP2PService::new(
+            executor,
+            libp2p_context,
+            custody_group_count,
+            secp256k1::Keypair::generate().into(),
+        )
+        .await
+        .expect("should build libp2p instance")
+        .0,
         signal,
     )
 }
```

### beacon_node/network/src/service.rs
```diff
@@ -12,6 +12,7 @@ use futures::future::OptionFuture;
 use futures::prelude::*;
 
 use lighthouse_network::Enr;
+use lighthouse_network::identity::Keypair;
 use lighthouse_network::rpc::InboundRequestId;
 use lighthouse_network::rpc::RequestType;
 use lighthouse_network::rpc::methods::RpcResponse;
@@ -212,6 +213,7 @@ impl<T: BeaconChainTypes> NetworkService<T> {
         executor: task_executor::TaskExecutor,
         libp2p_registry: Option<&'_ mut Registry>,
         beacon_processor_send: BeaconProcessorSend<T::EthSpec>,
+        local_keypair: Keypair,
     ) -> Result<
         (
             NetworkService<T>,
@@ -284,6 +286,7 @@ impl<T: BeaconChainTypes> NetworkService<T> {
                 .data_availability_checker
                 .custody_context()
                 .custody_group_count_at_head(&beacon_chain.spec),
+            local_keypair,
         )
         .await?;
 
@@ -366,13 +369,15 @@ impl<T: BeaconChainTypes> NetworkService<T> {
         executor: task_executor::TaskExecutor,
         libp2p_registry: Option<&'_ mut Registry>,
         beacon_processor_send: BeaconProcessorSend<T::EthSpec>,
+        local_keypair: Keypair,
     ) -> Result<(Arc<NetworkGlobals<T::EthSpec>>, NetworkSenders<T::EthSpec>), String> {
         let (network_service, network_globals, network_senders) = Self::build(
             beacon_chain,
             config,
             executor.clone(),
             libp2p_registry,
             beacon_processor_send,
+            local_keypair,
         )
         .await?;
 
```

### beacon_node/network/src/service/tests.rs
```diff
@@ -6,6 +6,7 @@ use beacon_chain::BeaconChainTypes;
 use beacon_chain::test_utils::BeaconChainHarness;
 use beacon_processor::{BeaconProcessorChannels, BeaconProcessorConfig};
 use futures::StreamExt;
+use lighthouse_network::identity::secp256k1;
 use lighthouse_network::types::{GossipEncoding, GossipKind};
 use lighthouse_network::{Enr, GossipTopic};
 use std::str::FromStr;
@@ -66,6 +67,7 @@ fn test_dht_persistence() {
             executor,
             None,
             beacon_processor_tx,
+            secp256k1::Keypair::generate().into(),
         )
         .await
         .unwrap();
@@ -134,6 +136,7 @@ fn test_removing_topic_weight_on_old_topics() {
             executor.clone(),
             None,
             beacon_processor_channels.beacon_processor_tx,
+            secp256k1::Keypair::generate().into(),
         )
         .await
         .unwrap()
```
