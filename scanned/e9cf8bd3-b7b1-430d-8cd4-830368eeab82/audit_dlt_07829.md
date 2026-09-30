# [?] Fix race condition in VC block proposal service (#1282)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2020-07-07
Source: https://github.com/sigp/lighthouse/commit/20a48df80aa62f453fe521767717f131773835ee
Type: security-commit

## Details
Fix race condition in VC block proposal service (#1282)

Closes #918
Closes #923

## Patch
### beacon_node/rest_api/src/validator.rs
```diff
@@ -16,7 +16,7 @@ use std::sync::Arc;
 use types::beacon_state::EthSpec;
 use types::{
     Attestation, AttestationData, BeaconState, Epoch, RelativeEpoch, SelectionProof,
-    SignedAggregateAndProof, SignedBeaconBlock, Slot, SubnetId,
+    SignedAggregateAndProof, SignedBeaconBlock, SubnetId,
 };
 
 /// HTTP Handler to retrieve the duties for a set of validators during a particular epoch. This
@@ -137,21 +137,22 @@ pub fn get_state_for_epoch<T: BeaconChainTypes>(
     config: StateSkipConfig,
 ) -> Result<BeaconState<T::EthSpec>, ApiError> {
     let slots_per_epoch = T::EthSpec::slots_per_epoch();
-    let head_epoch = beacon_chain.head()?.beacon_state.current_epoch();
+    let head = beacon_chain.head()?;
+    let current_epoch = beacon_chain.epoch()?;
+    let head_epoch = head.beacon_state.current_epoch();
 
-    if RelativeEpoch::from_epoch(head_epoch, epoch).is_ok() {
-        Ok(beacon_chain.head()?.beacon_state)
+    if head_epoch == current_epoch && RelativeEpoch::from_epoch(current_epoch, epoch).is_ok() {
+        Ok(head.beacon_state)
     } else {
-        let slot = if epoch > head_epoch {
-            // Move to the first slot of the epoch prior to the request.
-            //
-            // Taking advantage of saturating epoch subtraction.
+        // If epoch is ahead of current epoch, then it should be a "next epoch" request for
+        // attestation duties. So, go to the start slot of the epoch prior to that,
+        // which should be just the next wall-clock epoch.
+        let slot = if epoch > current_epoch {
             (epoch - 1).start_slot(slots_per_epoch)
-        } else {
-            // Move to the end of the epoch following the target.
-            //
-            // Taking advantage of saturating epoch subtraction.
-            (epoch + 2).start_slot(slots_per_epoch) - 1
+        }
+        // Otherwise, go to the start of the request epoch.
+        else {
+            epoch.start_slot(slots_per_epoch)
         };
 
         beacon_chain.state_at_slot(slot, config).map_err(|e| {
@@ -171,7 +172,6 @@ fn return_validator_duties<T: BeaconChainTypes>(
     let relative_epoch = RelativeEpoch::from_epoch(state.current_epoch(), epoch)
         .map_err(|_| ApiError::ServerError(String::from("Loaded state is in the wrong epoch")))?;
 
-    state.update_pubkey_cache()?;
     state
         .build_committee_cache(relative_epoch, &beacon_chain.spec)
         .map_err(|e| ApiError::ServerError(format!("Unable to build committee cache: {:?}", e)))?;
@@ -182,20 +182,26 @@ fn return_validator_duties<T: BeaconChainTypes>(
     // Get a list of all validators for this epoch.
     //
     // Used for quickly determining the slot for a proposer.
-    let validator_proposers: Vec<(usize, Slot)> = epoch
-        .slot_iter(T::EthSpec::slots_per_epoch())
-        .map(|slot| {
-            state
-                .get_beacon_proposer_index(slot, &beacon_chain.spec)
-                .map(|i| (i, slot))
-                .map_err(|e| {
-                    ApiError::ServerError(format!(
-                        "Unable to get proposer index for validator: {:?}",
-                        e
-                    ))
+    let validator_proposers = if epoch == state.current_epoch() {
+        Some(
+            epoch
+                .slot_iter(T::EthSpec::slots_per_epoch())
+                .map(|slot| {
+                    state
+                        .get_beacon_proposer_index(slot, &beacon_chain.spec)
+                        .map(|i| (i, slot))
+                        .map_err(|e| {
+                            ApiError::ServerError(format!(
+                                "Unable to get proposer index for validator: {:?}",
+                                e
+                            ))
+                        })
                 })
-        })
-        .collect::<Result<Vec<_>, _>>()?;
+                .collect::<Result<Vec<_>, _>>()?,
+        )
+    } else {
+        None
+    };
 
     validator_pubkeys
         .into_iter()
@@ -237,11 +243,13 @@ fn return_validator_duties<T: BeaconChainTypes>(
                         ApiError::ServerError(format!("Unable to find modulo: {:?}", e))
                     })?;
 
-                let block_proposal_slots = validator_proposers
-                    .iter()
-                    .filter(|(i, _slot)| validator_index == *i)
-                    .map(|(_i, slot)| *slot)
-                    .collect();
+                let block_proposal_slots = validator_proposers.as_ref().map(|proposers| {
+                    proposers
+                        .iter()
+                        .filter(|(i, _slot)| validator_index == *i)
+                        .map(|(_i, slot)| *slot)
+                        .collect()
+                });
 
                 Ok(ValidatorDutyBytes {
                     validator_pubkey,
@@ -260,8 +268,8 @@ fn return_validator_duties<T: BeaconChainTypes>(
                     attestation_slot: None,
                     attestation_committee_index: None,
                     attestation_committee_position: None,
+                    block_proposal_slots: None,
                     committee_count_at_slot: None,
-                    block_proposal_slots: vec![],
                     aggregator_modulo: None,
                 })
             }
```

### beacon_node/rest_api/tests/test.rs
```diff
@@ -337,6 +337,10 @@ fn check_duties<T: BeaconChainTypes>(
         "there should be a duty for each validator"
     );
 
+    // Are the duties from the current epoch of the beacon chain, and thus are proposer indices
+    // known?
+    let proposers_known = epoch == beacon_chain.epoch().unwrap();
+
     let mut state = beacon_chain
         .state_at_slot(
             epoch.start_slot(T::EthSpec::slots_per_epoch()),
@@ -380,38 +384,46 @@ fn check_duties<T: BeaconChainTypes>(
                 "attestation index should match"
             );
 
-            if !duty.block_proposal_slots.is_empty() {
-                for slot in &duty.block_proposal_slots {
-                    let expected_proposer = state
-                        .get_beacon_proposer_index(*slot, spec)
-                        .expect("should know proposer");
-                    assert_eq!(
-                        expected_proposer, validator_index,
-                        "should get correct proposal slot"
-                    );
+            if proposers_known {
+                let block_proposal_slots = duty.block_proposal_slots.as_ref().unwrap();
+
+                if !block_proposal_slots.is_empty() {
+                    for slot in block_proposal_slots {
+                        let expected_proposer = state
+                            .get_beacon_proposer_index(*slot, spec)
+                            .expect("should know proposer");
+                        assert_eq!(
+                            expected_proposer, validator_index,
+                            "should get correct proposal slot"
+                        );
+                    }
+                } else {
+                    epoch.slot_iter(E::slots_per_epoch()).for_each(|slot| {
+                        let slot_proposer = state
+                            .get_beacon_proposer_index(slot, spec)
+                            .expect("should know proposer");
+                        assert_ne!(
+                            slot_proposer, validator_index,
+                            "validator should not have proposal slot in this epoch"
+                        )
+                    })
                 }
             } else {
-                epoch.slot_iter(E::slots_per_epoch()).for_each(|slot| {
-                    let slot_proposer = state
-                        .get_beacon_proposer_index(slot, spec)
-                        .expect("should know proposer");
-                    assert_ne!(
-                        slot_proposer, validator_index,
-                        "validator should not have proposal slot in this epoch"
-                    )
-                })
+                assert_eq!(duty.block_proposal_slots, None);
             }
         });
 
-    // Validator duties should include a proposer for every slot of the epoch.
-    let mut all_proposer_slots: Vec<Slot> = duties
-        .iter()
-        .flat_map(|duty| duty.block_proposal_slots.clone())
-        .collect();
-    all_proposer_slots.sort();
+    if proposers_known {
+        // Validator duties should include a proposer for every slot of the epoch.
+        let mut all_proposer_slots: Vec<Slot> = duties
+            .iter()
+            .flat_map(|duty| duty.block_proposal_slots.clone().unwrap())
+            .collect();
+        all_proposer_slots.sort();
 
-    let all_slots: Vec<Slot> = epoch.slot_iter(E::slots_per_epoch()).collect();
-    assert_eq!(all_proposer_slots, all_slots);
+        let all_slots: Vec<Slot> = epoch.slot_iter(E::slots_per_epoch()).collect();
+        assert_eq!(all_proposer_slots, all_slots);
+    }
 }
 
 #[test]
```

### common/rest_types/src/validator.rs
```diff
@@ -10,9 +10,10 @@ pub type ValidatorDutyBytes = ValidatorDutyBase<PublicKeyBytes>;
 /// A validator duty with the pubkey represented as a `PublicKey`.
 pub type ValidatorDuty = ValidatorDutyBase<PublicKey>;
 
+// NOTE: if you add or remove fields, please adjust `eq_ignoring_proposal_slots`
 #[derive(PartialEq, Debug, Serialize, Deserialize, Clone)]
 pub struct ValidatorDutyBase<T> {
-    /// The validator's BLS public key, uniquely identifying them. _48-bytes, hex encoded with 0x prefix, case insensitive._
+    /// The validator's BLS public key, uniquely identifying them.
     pub validator_pubkey: T,
     /// The validator's index in `state.validators`
     pub validator_index: Option<u64>,
@@ -25,7 +26,9 @@ pub struct ValidatorDutyBase<T> {
     /// The committee count at `attestation_slot`.
     pub committee_count_at_slot: Option<u64>,
     /// The slots in which a validator must propose a block (can be empty).
-    pub block_proposal_slots: Vec<Slot>,
+    ///
+    /// Should be set to `None` when duties are not yet known (before the current epoch).
+    pub block_proposal_slots: Option<Vec<Slot>>,
     /// This provides the modulo: `max(1, len(committee) // TARGET_AGGREGATORS_PER_COMMITTEE)`
     /// which allows the validator client to determine if this duty requires the validator to be
     /// aggregate attestations.
@@ -49,6 +52,20 @@ impl<T> ValidatorDutyBase<T> {
             false
         }
     }
+
+    /// Return `true` if these validator duties are equal, ignoring their `block_proposal_slots`.
+    pub fn eq_ignoring_proposal_slots(&self, other: &Self) -> bool
+    where
+        T: PartialEq,
+    {
+        self.validator_pubkey == other.validator_pubkey
+            && self.validator_index == other.validator_index
+            && self.attestation_slot == other.attestation_slot
+            && self.attestation_committee_index == other.attestation_committee_index
+            && self.attestation_committee_position == other.attestation_committee_position
+            && self.committee_count_at_slot == other.committee_count_at_slot
+            && self.aggregator_modulo == other.aggregator_modulo
+    }
 }
 
 #[derive(PartialEq, Debug, Serialize, Deserialize, Clone, Encode, Decode)]
@@ -74,3 +91,29 @@ pub struct ValidatorSubscription {
     /// for this slot.
     pub is_aggregator: bool,
 }
+
+#[cfg(test)]
+mod test {
+    use super::*;
+
+    #[test]
+    fn eq_ignoring_proposal_slots() {
+        let duty1 = ValidatorDuty {
+            validator_pubkey: PublicKey::default(),
+            validator_index: Some(10),
+            attestation_slot: Some(Slot::new(50)),
+            attestation_committee_index: Some(2),
+            attestation_committee_position: Some(6),
+            committee_count_at_slot: Some(4),
+            block_proposal_slots: None,
+            aggregator_modulo: Some(99),
+        };
+        let duty2 = ValidatorDuty {
+            block_proposal_slots: Some(vec![Slot::new(42), Slot::new(45)]),
+            ..duty1.clone()
+        };
+        assert_ne!(duty1, duty2);
+        assert!(duty1.eq_ignoring_proposal_slots(&duty2));
+        assert!(duty2.eq_ignoring_proposal_slots(&duty1));
+    }
+}
```

### consensus/types/src/beacon_state.rs
```diff
@@ -510,7 +510,13 @@ impl<T: EthSpec> BeaconState<T> {
     ///
     /// Spec v0.12.1
     pub fn get_beacon_proposer_index(&self, slot: Slot, spec: &ChainSpec) -> Result<usize, Error> {
+        // Proposer indices are only known for the current epoch, due to the dependence on the
+        // effective balances of validators, which change at every epoch transition.
         let epoch = slot.epoch(T::slots_per_epoch());
+        if epoch != self.current_epoch() {
+            return Err(Error::SlotOutOfBounds);
+        }
+
         let seed = self.get_beacon_proposer_seed(slot, spec)?;
         let indices = self.get_active_validator_indices(epoch, spec)?;
 
```

### consensus/types/src/beacon_state/tests.rs
```diff
@@ -95,7 +95,7 @@ fn test_cache_initialization<'a, T: EthSpec>(
     state.build_committee_cache(relative_epoch, spec).unwrap();
 
     // Assert a call to a cache-using function passes.
-    let _ = state.get_beacon_proposer_index(slot, spec).unwrap();
+    state.get_beacon_committee(slot, 0).unwrap();
 
     // Drop the cache.
     state.drop_committee_cache(relative_epoch);
```

### testing/simulator/src/checks.rs
```diff
@@ -126,3 +126,23 @@ async fn verify_validator_count<E: EthSpec>(
         Ok(())
     }
 }
+
+/// Verifies that there's been a block produced at every slot up to and including `slot`.
+pub async fn verify_full_block_production_up_to<E: EthSpec>(
+    network: LocalNetwork<E>,
+    slot: Slot,
+    slot_duration: Duration,
+) -> Result<(), String> {
+    slot_delay(slot, slot_duration).await;
+    let beacon_nodes = network.beacon_nodes.read();
+    let beacon_chain = beacon_nodes[0].client.beacon_chain().unwrap();
+    let chain_dump = beacon_chain.chain_dump().unwrap();
+    if chain_dump.len() != slot.as_usize() + 1 {
+        return Err(format!(
+            "There wasn't a block produced at every slot, got: {}, expected: {}",
+            chain_dump.len(),
+            slot.as_usize() + 1
+        ));
+    }
+    Ok(())
+}
```

### testing/simulator/src/eth1_sim.rs
```diff
@@ -9,6 +9,7 @@ use node_test_rig::{
 use rayon::prelude::*;
 use std::net::{IpAddr, Ipv4Addr};
 use std::time::Duration;
+use types::{Epoch, EthSpec, MainnetEthSpec};
 
 pub fn run_eth1_sim(matches: &ArgMatches) -> Result<(), String> {
     let node_count = value_t!(matches, "nodes", usize).expect("missing nodes default");
@@ -146,9 +147,15 @@ pub fn run_eth1_sim(matches: &ArgMatches) -> Result<(), String> {
          * tests start at the right time. Whilst this is works well for now, it's subject to
          * breakage by changes to the VC.
          */
-        let (finalization, validator_count, onboarding) = futures::join!(
+        let (finalization, block_prod, validator_count, onboarding) = futures::join!(
             // Check that the chain finalizes at the first given opportunity.
             checks::verify_first_finalization(network.clone(), slot_duration),
+            // Check that a block is produced at every slot.
+            checks::verify_full_block_production_up_to(
+                network.clone(),
+                Epoch::new(4).start_slot(MainnetEthSpec::slots_per_epoch()),
+                slot_duration,
+            ),
             // Check that the chain starts with the expected validator count.
             checks::verify_initial_validator_count(
                 network.clone(),
@@ -164,6 +171,7 @@ pub fn run_eth1_sim(matches: &ArgMatches) -> Result<(), String> {
             )
         );
 
+        block_prod?;
         finalization?;
         validator_count?;
         onboarding?;
```

### testing/simulator/src/local_network.rs
```diff
@@ -11,9 +11,9 @@ const BOOTNODE_PORT: u16 = 42424;
 
 /// Helper struct to reduce `Arc` usage.
 pub struct Inner<E: EthSpec> {
-    context: RuntimeContext<E>,
-    beacon_nodes: RwLock<Vec<LocalBeaconNode<E>>>,
-    validator_clients: RwLock<Vec<LocalValidatorClient<E>>>,
+    pub context: RuntimeContext<E>,
+    pub beacon_nodes: RwLock<Vec<LocalBeaconNode<E>>>,
+    pub validator_clients: RwLock<Vec<LocalValidatorClient<E>>>,
 }
 
 /// Represents a set of interconnected `LocalBeaconNode` and `LocalValidatorClient`.
```

### testing/simulator/src/no_eth1_sim.rs
```diff
@@ -9,6 +9,7 @@ use rayon::prelude::*;
 use std::net::{IpAddr, Ipv4Addr};
 use std::time::{Duration, SystemTime, UNIX_EPOCH};
 use tokio::time::{delay_until, Instant};
+use types::{Epoch, EthSpec, MainnetEthSpec};
 
 pub fn run_no_eth1_sim(matches: &ArgMatches) -> Result<(), String> {
     let node_count = value_t!(matches, "nodes", usize).expect("missing nodes default");
@@ -121,8 +122,18 @@ pub fn run_no_eth1_sim(matches: &ArgMatches) -> Result<(), String> {
         let checks_fut = async {
             delay_until(genesis_instant).await;
 
-            // Check that the chain finalizes at the first given opportunity.
-            checks::verify_first_finalization(network.clone(), slot_duration).await?;
+            let (finalization, block_prod) = futures::join!(
+                // Check that the chain finalizes at the first given opportunity.
+                checks::verify_first_finalization(network.clone(), slot_duration),
+                // Check that a block is produced at every slot.
+                checks::verify_full_block_production_up_to(
+                    network.clone(),
+                    Epoch::new(4).start_slot(MainnetEthSpec::slots_per_epoch()),
+                    slot_duration,
+                )
+            );
+            finalization?;
+            block_prod?;
 
             Ok::<(), String>(())
         };
```

### validator_client/src/block_service.rs
```diff
@@ -1,20 +1,16 @@
-use crate::{duties_service::DutiesService, validator_store::ValidatorStore};
+use crate::validator_store::ValidatorStore;
 use environment::RuntimeContext;
+use futures::channel::mpsc::Receiver;
 use futures::{StreamExt, TryFutureExt};
 use remote_beacon_node::{PublishStatus, RemoteBeaconNode};
-use slog::{crit, error, info, trace};
+use slog::{crit, debug, error, info, trace, warn};
 use slot_clock::SlotClock;
 use std::ops::Deref;
 use std::sync::Arc;
-use tokio::time::{interval_at, Duration, Instant};
-use types::{ChainSpec, EthSpec, PublicKey, Slot};
-
-/// Delay this period of time after the slot starts. This allows the node to process the new slot.
-const TIME_DELAY_FROM_SLOT: Duration = Duration::from_millis(100);
+use types::{EthSpec, PublicKey, Slot};
 
 /// Builds a `BlockService`.
 pub struct BlockServiceBuilder<T, E: EthSpec> {
-    duties_service: Option<DutiesService<T, E>>,
     validator_store: Option<ValidatorStore<T, E>>,
     slot_clock: Option<Arc<T>>,
     beacon_node: Option<RemoteBeaconNode<E>>,
@@ -24,19 +20,13 @@ pub struct BlockServiceBuilder<T, E: EthSpec> {
 impl<T: SlotClock + 'static, E: EthSpec> BlockServiceBuilder<T, E> {
     pub fn new() -> Self {
         Self {
-            duties_service: None,
             validator_store: None,
             slot_clock: None,
             beacon_node: None,
             context: None,
         }
     }
 
-    pub fn duties_service(mut self, service: DutiesService<T, E>) -> Self {
-        self.duties_service = Some(service);
-        self
-    }
-
     pub fn validator_store(mut self, store: ValidatorStore<T, E>) -> Self {
         self.validator_store = Some(store);
         self
@@ -60,9 +50,6 @@ impl<T: SlotClock + 'static, E: EthSpec> BlockServiceBuilder<T, E> {
     pub fn build(self) -> Result<BlockService<T, E>, String> {
         Ok(BlockService {
             inner: Arc::new(Inner {
-                duties_service: self
-                    .duties_service
-                    .ok_or_else(|| "Cannot build BlockService without duties_service")?,
                 validator_store: self
                     .validator_store
                     .ok_or_else(|| "Cannot build BlockService without validator_store")?,
@@ -82,7 +69,6 @@ impl<T: SlotClock + 'static, E: EthSpec> BlockServiceBuilder<T, E> {
 
 /// Helper to minimise `Arc` usage.
 pub struct Inner<T, E: EthSpec> {
-    duties_service: DutiesService<T, E>,
     validator_store: ValidatorStore<T, E>,
     slot_clock: Arc<T>,
     beacon_node: RemoteBeaconNode<E>,
@@ -110,77 +96,88 @@ impl<T, E: EthSpec> Deref for BlockService<T, E> {
     }
 }
 
+/// Notification from the duties service that we should try to produce a block.
+pub struct BlockServiceNotification {
+    pub slot: Slot,
+    pub block_proposers: Vec<PublicKey>,
+}
+
 impl<T: SlotClock + 'static, E: EthSpec> BlockService<T, E> {
-    /// Starts the service that periodically attempts to produce blocks.
-    pub fn start_update_service(self, spec: &ChainSpec) -> Result<(), String> {
+    pub fn start_update_service(
+        self,
+        notification_rx: Receiver<BlockServiceNotification>,
+    ) -> Result<(), String> {
         let log = self.context.log().clone();
 
-        let duration_to_next_slot = self
-            .slot_clock
-            .duration_to_next_slot()
-            .ok_or_else(|| "Unable to determine duration to next slot".to_string())?;
-
-        info!(
-            log,
-            "Block production service started";
-            "next_update_millis" => duration_to_next_slot.as_millis()
-        );
-
-        let mut interval = {
-            let slot_duration = Duration::from_millis(spec.milliseconds_per_slot);
-            // Note: interval_at panics if slot_duration = 0
-            interval_at(
-                Instant::now() + duration_to_next_slot + TIME_DELAY_FROM_SLOT,
-                slot_duration,
-            )
-        };
+        info!(log, "Block production service started");
 
         let executor = self.inner.context.executor.clone();
 
-        let interval_fut = async move {
-            while interval.next().await.is_some() {
-                self.do_update().await.ok();
+        let block_service_fut = notification_rx.for_each(move |notif| {
+            let service = self.clone();
+            async move {
+                service.do_update(notif).await.ok();
             }
-        };
+        });
 
-        executor.spawn(interval_fut, "block_service");
+        executor.spawn(block_service_fut, "block_service");
 
         Ok(())
     }
 
     /// Attempt to produce a block for any block producers in the `ValidatorStore`.
-    async fn do_update(&self) -> Result<(), ()> {
+    async fn do_update(&self, notification: BlockServiceNotification) -> Result<(), ()> {
         let log = self.context.log();
 
         let slot = self.slot_clock.now().ok_or_else(move || {
             crit!(log, "Duties manager failed to read slot clock");
         })?;
 
+        if notification.slot != slot {
+            warn!(
+                log,
+                "Skipping block production for expired slot";
+                "current_slot" => slot.as_u64(),
+                "notification_slot" => notification.slot.as_u64(),
+                "info" => "Your machine could be overloaded"
+            );
+            return Ok(());
+        }
+
+        if slot == self.context.eth2_config.spec.genesis_slot {
+            debug!(
+                log,
+                "Not producing block at genesis slot";
+                "proposers" => format!("{:?}", notification.block_proposers),
+            );
+            return Ok(());
+        }
+
         trace!(
             log,
             "Block service update started";
             "slot" => slot.as_u64()
         );
 
-        let iter = self.duties_service.block_producers(slot).into_iter();
+        let proposers = notification.block_proposers;
 
-        if iter.len() == 0 {
+        if proposers.is_empty() {
             trace!(
                 log,
                 "No local block proposers for this slot";
                 "slot" => slot.as_u64()
             )
-        } else if iter.len() > 1 {
+        } else if proposers.len() > 1 {
             error!(
                 log,
                 "Multiple block proposers for this slot";
                 "action" => "producing blocks for all proposers",
-                "num_proposers" => iter.len(),
+                "num_proposers" => proposers.len(),
                 "slot" => slot.as_u64(),
             )
         }
 
-        iter.for_each(|validator_pubkey| {
+        proposers.into_iter().for_each(|validator_pubkey| {
             let service = self.clone();
             let log = log.clone();
             self.inner.context.executor.runtime_handle().spawn(
```

### validator_client/src/duties_service.rs
```diff
@@ -1,6 +1,9 @@
-use crate::{is_synced::is_synced, validator_store::ValidatorStore};
+use crate::{
+    block_service::BlockServiceNotification, is_synced::is_synced, validator_store::ValidatorStore,
+};
 use environment::RuntimeContext;
-use futures::StreamExt;
+use futures::channel::mpsc::Sender;
+use futures::{SinkExt, StreamExt};
 use parking_lot::RwLock;
 use remote_beacon_node::{PublishStatus, RemoteBeaconNode};
 use rest_types::{ValidatorDuty, ValidatorDutyBytes, ValidatorSubscription};
@@ -137,6 +140,8 @@ enum InsertOutcome {
     NewEpoch,
     /// The duties were identical to some already in the store.
     Identical,
+    /// The duties informed us of new proposal slots but were otherwise identical.
+    NewProposalSlots,
     /// There were duties for this validator and epoch in the store that were different to the ones
     /// provided. The existing duties were replaced.
     Replaced { should_resubscribe: bool },
@@ -149,10 +154,10 @@ impl InsertOutcome {
     pub fn is_subscription_candidate(self) -> bool {
         match self {
             InsertOutcome::Replaced { should_resubscribe } => should_resubscribe,
-            InsertOutcome::NewValidator => true,
-            InsertOutcome::NewEpoch => true,
-            InsertOutcome::Identical => false,
-            InsertOutcome::Invalid => false,
+            InsertOutcome::NewValidator | InsertOutcome::NewEpoch => true,
+            InsertOutcome::Identical | InsertOutcome::Invalid | InsertOutcome::NewProposalSlots => {
+                false
+            }
         }
     }
 }
@@ -171,8 +176,14 @@ impl DutiesStore {
             .filter(|(_validator_pubkey, validator_map)| {
                 validator_map
                     .get(&epoch)
-                    .map(|duties| !duties.duty.block_proposal_slots.is_empty())
-                    .unwrap_or_else(|| false)
+                    .map(|duties| {
+                        duties
+                            .duty
+                            .block_proposal_slots
+                            .as_ref()
+                            .map_or(false, |proposal_slots| !proposal_slots.is_empty())
+                    })
+                    .unwrap_or(false)
             })
             .count()
     }
@@ -191,7 +202,7 @@ impl DutiesStore {
             .count()
     }
 
-    fn block_producers(&self, slot: Slot, slots_per_epoch: u64) -> Vec<PublicKey> {
+    fn block_proposers(&self, slot: Slot, slots_per_epoch: u64) -> Vec<PublicKey> {
         self.store
             .read()
             .iter()
@@ -201,7 +212,7 @@ impl DutiesStore {
                 let epoch = slot.epoch(slots_per_epoch);
 
                 validator_map.get(&epoch).and_then(|duties| {
-                    if duties.duty.block_proposal_slots.contains(&slot) {
+                    if duties.duty.block_proposal_slots.as_ref()?.contains(&slot) {
                         Some(duties.duty.validator_pubkey.clone())
                     } else {
                         None
@@ -260,8 +271,15 @@ impl DutiesStore {
 
         if let Some(validator_map) = store.get_mut(&duties.duty.validator_pubkey) {
             if let Some(known_duties) = validator_map.get_mut(&epoch) {
-                if known_duties.duty == duties.duty {
-                    Ok(InsertOutcome::Identical)
+                if known_duties.duty.eq_ignoring_proposal_slots(&duties.duty) {
+                    if known_duties.duty.block_proposal_slots == duties.duty.block_proposal_slots {
+                        Ok(InsertOutcome::Identical)
+                    } else if duties.duty.block_proposal_slots.is_some() {
+                        known_duties.duty.block_proposal_slots = duties.duty.block_proposal_slots;
+                        Ok(InsertOutcome::NewProposalSlots)
+                    } else {
+                        Ok(InsertOutcome::Invalid)
+                    }
                 } else {
                     // Compute the selection proof.
                     duties.compute_selection_proof(validator_store)?;
@@ -388,8 +406,9 @@ pub struct Inner<T, E: EthSpec> {
 
 /// Maintains a store of the duties for all voting validators in the `validator_store`.
 ///
-/// Polls the beacon node at the start of each epoch, collecting duties for the current and next
-/// epoch.
+/// Polls the beacon node at the start of each slot, collecting duties for the current and next
+/// epoch. The duties service notifies the block production service to run each time it completes,
+/// so it *must* be run every slot.
 pub struct DutiesService<T, E: EthSpec> {
     inner: Arc<Inner<T, E>>,
 }
@@ -430,8 +449,8 @@ impl<T: SlotClock + 'static, E: EthSpec> DutiesService<T, E> {
     ///
     /// It is possible that multiple validators have an identical proposal slot, however that is
     /// likely the result of heavy forking (lol) or inconsistent beacon node connections.
-    pub fn block_producers(&self, slot: Slot) -> Vec<PublicKey> {
-        self.store.block_producers(slot, E::slots_per_epoch())
+    pub fn block_proposers(&self, slot: Slot) -> Vec<PublicKey> {
+        self.store.block_proposers(slot, E::slots_per_epoch())
     }
 
     /// Returns all `ValidatorDuty` for the given `slot`.
@@ -440,7 +459,11 @@ impl<T: SlotClock + 'static, E: EthSpec> DutiesService<T, E> {
     }
 
     /// Start the service that periodically polls the beacon node for validator duties.
-    pub fn start_update_service(self, spec: &ChainSpec) -> Result<(), String> {
+    pub fn start_update_service(
+        self,
+        mut block_service_tx: Sender<BlockServiceNotification>,
+        spec: &ChainSpec,
+    ) -> Result<(), String> {
         let duration_to_next_slot = self
             .slot_clock
             .duration_to_next_slot()
@@ -456,17 +479,19 @@ impl<T: SlotClock + 'static, E: EthSpec> DutiesService<T, E> {
         };
 
         // Run an immediate update before starting the updater service.
+        let duties_service = self.clone();
+        let mut block_service_tx_clone = block_service_tx.clone();
         self.inner
             .context
             .executor
             .runtime_handle()
-            .spawn(self.clone().do_update());
+            .spawn(async move { duties_service.do_update(&mut block_service_tx_clone).await });
 
         let executor = self.inner.context.executor.clone();
 
         let interval_fut = async move {
             while interval.next().await.is_some() {
-                self.clone().do_update().await.ok();
+                self.clone().do_update(&mut block_service_tx).await;
             }
         };
 
@@ -476,61 +501,70 @@ impl<T: SlotClock + 'static, E: EthSpec> DutiesService<T, E> {
     }
 
     /// Attempt to download the duties of all managed validators for this epoch and the next.
-    async fn do_update(self) -> Result<(), ()> {
+    async fn do_update(self, block_service_tx: &mut Sender<BlockServiceNotification>) {
         let log = self.context.log();
 
         if !is_synced(&self.beacon_node, &self.slot_clock, None).await
             && !self.allow_unsynced_beacon_node
         {
-            return Ok(());
+            return;
         }
 
-        let current_epoch = self
-            .slot_clock
-            .now()
-            .ok_or_else(|| {
-                error!(log, "Duties manager failed to read slot clock");
-            })
-            .map(|slot| {
-                let epoch = slot.epoch(E::slots_per_epoch());
+        let slot = if let Some(slot) = self.slot_clock.now() {
+            slot
+        } else {
+            error!(log, "Duties manager failed to read slot clock");
+            return;
+        };
 
-                if slot % E::slots_per_epoch() == 0 {
-                    let prune_below = epoch - PRUNE_DEPTH;
+        let current_epoch = slot.epoch(E::slots_per_epoch());
 
-                    trace!(
-                        log,
-                        "Pruning duties cache";
-                        "pruning_below" => prune_below.as_u64(),
-                        "current_epoch" => epoch.as_u64(),
-                    );
+        if slot % E::slots_per_epoch() == 0 {
+            let prune_below = current_epoch - PRUNE_DEPTH;
 
-                    self.store.prune(prune_below);
-                }
+            trace!(
+                log,
+                "Pruning duties cache";
+                "pruning_below" => prune_below.as_u64(),
+                "current_epoch" => current_epoch.as_u64(),
+            );
 
-                epoch
-            })?;
+            self.store.prune(prune_below);
+        }
 
-        let result = self.clone().update_epoch(current_epoch).await;
-        if let Err(e) = result {
+        // Update duties for the current epoch, but keep running if there's an error:
+        // block production or the next epoch update could still succeed.
+        if let Err(e) = self.clone().update_epoch(current_epoch).await {
             error!(
                 log,
                 "Failed to get current epoch duties";
                 "http_error" => format!("{:?}", e)
             );
         }
 
-        self.clone()
-            .update_epoch(current_epoch + 1)
+        // Notify the block service to produce a block.
+        if let Err(e) = block_service_tx
+            .send(BlockServiceNotification {
+                slot,
+                block_proposers: self.block_proposers(slot),
+            })
             .await
-            .map_err(move |e| {
-                error!(
-                    log,
-                    "Failed to get next epoch duties";
-                    "http_error" => format!("{:?}", e)
-                );
-            })?;
+        {
+            error!(
+                log,
+                "Failed to notify block service";
+                "error" => format!("{:?}", e)
+            );
+        };
 
-        Ok(())
+        // Update duties for the next epoch.
+        if let Err(e) = self.clone().update_epoch(current_epoch + 1).await {
+            error!(
+                log,
+                "Failed to get next epoch duties";
+                "http_error" => format!("{:?}", e)
+            );
+        }
     }
 
     /// Attempt to download the duties of all managed validators for the given `epoch`.
@@ -548,6 +582,7 @@ impl<T: SlotClock + 'static, E: EthSpec> DutiesService<T, E> {
 
         let mut new_validator = 0;
         let mut new_epoch = 0;
+        let mut new_proposal_slots = 0;
         let mut identical = 0;
         let mut replaced = 0;
         let mut invalid = 0;
@@ -596,6 +631,7 @@ impl<T: SlotClock + 'static, E: EthSpec> DutiesService<T, E> {
                         );
                         new_validator += 1;
                     }
+                    InsertOutcome::NewProposalSlots => new_proposal_slots += 1,
                     InsertOutcome::NewEpoch => new_epoch += 1,
                     InsertOutcome::Identical => identical += 1,
                     InsertOutcome::Replaced { .. } => replaced += 1,
@@ -634,6 +670,7 @@ impl<T: SlotClock + 'static, E: EthSpec> DutiesService<T, E> {
             "Performed duties update";
             "identical" => identical,
             "new_epoch" => new_epoch,
+            "new_proposal_slots" => new_proposal_slots,
             "new_validator" => new_validator,
             "replaced" => replaced,
             "epoch" => format!("{}", epoch)
@@ -643,7 +680,8 @@ impl<T: SlotClock + 'static, E: EthSpec> DutiesService<T, E> {
             warn!(
                 log,
                 "Duties changed during routine update";
-                "info" => "Chain re-org likely occurred"
+                "info" => "Chain re-org likely occurred",
+                "replaced" => replaced,
             )
         }
 
@@ -688,8 +726,9 @@ fn duties_match_epoch(duties: &ValidatorDuty, epoch: Epoch, slots_per_epoch: u64
     duties
         .attestation_slot
         .map_or(true, |slot| slot.epoch(slots_per_epoch) == epoch)
-        && duties
-            .block_proposal_slots
-            .iter()
-            .all(|slot| slot.epoch(slots_per_epoch) == epoch)
+        && duties.block_proposal_slots.as_ref().map_or(true, |slots| {
+            slots
+                .iter()
+                .all(|slot| slot.epoch(slots_per_epoch) == epoch)
+        })
 }
```

### validator_client/src/lib.rs
```diff
@@ -18,6 +18,7 @@ use config::SLASHING_PROTECTION_FILENAME;
 use duties_service::{DutiesService, DutiesServiceBuilder};
 use environment::RuntimeContext;
 use fork_service::{ForkService, ForkServiceBuilder};
+use futures::channel::mpsc;
 use notifier::spawn_notifier;
 use remote_beacon_node::RemoteBeaconNode;
 use slog::{error, info, warn, Logger};
@@ -208,7 +209,6 @@ impl<T: EthSpec> ProductionValidatorClient<T> {
             .build()?;
 
         let block_service = BlockServiceBuilder::new()
-            .duties_service(duties_service.clone())
             .slot_clock(slot_clock.clone())
             .validator_store(validator_store.clone())
             .beacon_node(beacon_node.clone())
@@ -234,9 +234,15 @@ impl<T: EthSpec> ProductionValidatorClient<T> {
     }
 
     pub fn start_service(&mut self) -> Result<(), String> {
+        // We use `SLOTS_PER_EPOCH` as the capacity of the block notification channel, because
+        // we don't except notifications to be delayed by more than a single slot, let alone a
+        // whole epoch!
+        let channel_capacity = T::slots_per_epoch() as usize;
+        let (block_service_tx, block_service_rx) = mpsc::channel(channel_capacity);
+
         self.duties_service
             .clone()
-            .start_update_service(&self.context.eth2_config.spec)
+            .start_update_service(block_service_tx, &self.context.eth2_config.spec)
             .map_err(|e| format!("Unable to start duties service: {}", e))?;
 
         self.fork_service
@@ -246,7 +252,7 @@ impl<T: EthSpec> ProductionValidatorClient<T> {
 
         self.block_service
             .clone()
-            .start_update_service(&self.context.eth2_config.spec)
+            .start_update_service(block_service_rx)
             .map_err(|e| format!("Unable to start block service: {}", e))?;
 
         self.attestation_service
```
