# [?] Fix race condition in seen caches (#1937)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2020-11-22
Source: https://github.com/sigp/lighthouse/commit/426b3001e06daacfad3d68e6ba27bb07ef442444
Type: security-commit

## Details
Fix race condition in seen caches (#1937)

## Issue Addressed

Closes #1719

## Proposed Changes

Lift the internal `RwLock`s and `Mutex`es from the `Observed*` data structures to resolve the race conditions described in #1719.

Most of this work was done by @paulhauner on his `lift-locks` branch, I merely updated it for the current `master` and checked over it.

## Additional Info

I think it would be prudent to test this on a testnet or two before mainnet launch, just to be sure that the extra lock contention doesn't negatively impact performance.

## Patch
### beacon_node/beacon_chain/src/attestation_verification.rs
```diff
@@ -316,6 +316,7 @@ impl<T: BeaconChainTypes> VerifiedAggregatedAttestation<T> {
         let attestation_root = attestation.tree_hash_root();
         if chain
             .observed_attestations
+            .write()
             .is_known(attestation, attestation_root)
             .map_err(|e| Error::BeaconChainError(e.into()))?
         {
@@ -329,6 +330,7 @@ impl<T: BeaconChainTypes> VerifiedAggregatedAttestation<T> {
         // Note: do not observe yet, only observe once the attestation has been verfied.
         match chain
             .observed_aggregators
+            .read()
             .validator_has_been_observed(attestation, aggregator_index as usize)
         {
             Ok(true) => Err(Error::AggregatorAlreadyKnown(aggregator_index)),
@@ -400,6 +402,7 @@ impl<T: BeaconChainTypes> VerifiedAggregatedAttestation<T> {
         // attestations processed at the same time could be published.
         if let ObserveOutcome::AlreadyKnown = chain
             .observed_attestations
+            .write()
             .observe_attestation(attestation, Some(attestation_root))
             .map_err(|e| Error::BeaconChainError(e.into()))?
         {
@@ -412,6 +415,7 @@ impl<T: BeaconChainTypes> VerifiedAggregatedAttestation<T> {
         // attestations processed at the same time could be published.
         if chain
             .observed_aggregators
+            .write()
             .observe_validator(&attestation, aggregator_index as usize)
             .map_err(BeaconChainError::from)?
         {
@@ -518,6 +522,7 @@ impl<T: BeaconChainTypes> VerifiedUnaggregatedAttestation<T> {
          */
         if chain
             .observed_attesters
+            .read()
             .validator_has_been_observed(&attestation, validator_index as usize)
             .map_err(BeaconChainError::from)?
         {
@@ -538,6 +543,7 @@ impl<T: BeaconChainTypes> VerifiedUnaggregatedAttestation<T> {
         // process them in different threads.
         if chain
             .observed_attesters
+            .write()
             .observe_validator(&attestation, validator_index as usize)
             .map_err(BeaconChainError::from)?
         {
```

### beacon_node/beacon_chain/src/beacon_chain.rs
```diff
@@ -31,7 +31,7 @@ use fork_choice::ForkChoice;
 use futures::channel::mpsc::Sender;
 use itertools::process_results;
 use operation_pool::{OperationPool, PersistedOperationPool};
-use parking_lot::RwLock;
+use parking_lot::{Mutex, RwLock};
 use slog::{crit, debug, error, info, trace, warn, Logger};
 use slot_clock::SlotClock;
 use state_processing::{
@@ -181,20 +181,21 @@ pub struct BeaconChain<T: BeaconChainTypes> {
     /// a method to get an aggregated `Attestation` for some `AttestationData`.
     pub naive_aggregation_pool: RwLock<NaiveAggregationPool<T::EthSpec>>,
     /// Contains a store of attestations which have been observed by the beacon chain.
-    pub observed_attestations: ObservedAttestations<T::EthSpec>,
+    pub(crate) observed_attestations: RwLock<ObservedAttestations<T::EthSpec>>,
     /// Maintains a record of which validators have been seen to attest in recent epochs.
-    pub observed_attesters: ObservedAttesters<T::EthSpec>,
+    pub(crate) observed_attesters: RwLock<ObservedAttesters<T::EthSpec>>,
     /// Maintains a record of which validators have been seen to create `SignedAggregateAndProofs`
     /// in recent epochs.
-    pub observed_aggregators: ObservedAggregators<T::EthSpec>,
+    pub(crate) observed_aggregators: RwLock<ObservedAggregators<T::EthSpec>>,
     /// Maintains a record of which validators have proposed blocks for each slot.
-    pub observed_block_producers: ObservedBlockProducers<T::EthSpec>,
+    pub(crate) observed_block_producers: RwLock<ObservedBlockProducers<T::EthSpec>>,
     /// Maintains a record of which validators have submitted voluntary exits.
-    pub observed_voluntary_exits: ObservedOperations<SignedVoluntaryExit, T::EthSpec>,
+    pub(crate) observed_voluntary_exits: Mutex<ObservedOperations<SignedVoluntaryExit, T::EthSpec>>,
     /// Maintains a record of which validators we've seen proposer slashings for.
-    pub observed_proposer_slashings: ObservedOperations<ProposerSlashing, T::EthSpec>,
+    pub(crate) observed_proposer_slashings: Mutex<ObservedOperations<ProposerSlashing, T::EthSpec>>,
     /// Maintains a record of which validators we've seen attester slashings for.
-    pub observed_attester_slashings: ObservedOperations<AttesterSlashing<T::EthSpec>, T::EthSpec>,
+    pub(crate) observed_attester_slashings:
+        Mutex<ObservedOperations<AttesterSlashing<T::EthSpec>, T::EthSpec>>,
     /// Provides information from the Ethereum 1 (PoW) chain.
     pub eth1_chain: Option<Eth1Chain<T::Eth1Chain, T::EthSpec>>,
     /// Stores a "snapshot" of the chain at the time the head-of-the-chain block was received.
@@ -1158,9 +1159,11 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
     ) -> Result<ObservationOutcome<SignedVoluntaryExit>, Error> {
         // NOTE: this could be more efficient if it avoided cloning the head state
         let wall_clock_state = self.wall_clock_state()?;
-        Ok(self
-            .observed_voluntary_exits
-            .verify_and_observe(exit, &wall_clock_state, &self.spec)?)
+        Ok(self.observed_voluntary_exits.lock().verify_and_observe(
+            exit,
+            &wall_clock_state,
+            &self.spec,
+        )?)
     }
 
     /// Accept a pre-verified exit and queue it for inclusion in an appropriate block.
@@ -1176,7 +1179,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         proposer_slashing: ProposerSlashing,
     ) -> Result<ObservationOutcome<ProposerSlashing>, Error> {
         let wall_clock_state = self.wall_clock_state()?;
-        Ok(self.observed_proposer_slashings.verify_and_observe(
+        Ok(self.observed_proposer_slashings.lock().verify_and_observe(
             proposer_slashing,
             &wall_clock_state,
             &self.spec,
@@ -1196,7 +1199,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         attester_slashing: AttesterSlashing<T::EthSpec>,
     ) -> Result<ObservationOutcome<AttesterSlashing<T::EthSpec>>, Error> {
         let wall_clock_state = self.wall_clock_state()?;
-        Ok(self.observed_attester_slashings.verify_and_observe(
+        Ok(self.observed_attester_slashings.lock().verify_and_observe(
             attester_slashing,
             &wall_clock_state,
             &self.spec,
@@ -1506,7 +1509,11 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         // Iterate through the attestations in the block and register them as an "observed
         // attestation". This will stop us from propagating them on the gossip network.
         for a in &signed_block.message.body.attestations {
-            match self.observed_attestations.observe_attestation(a, None) {
+            match self
+                .observed_attestations
+                .write()
+                .observe_attestation(a, None)
+            {
                 // If the observation was successful or if the slot for the attestation was too
                 // low, continue.
                 //
@@ -2091,7 +2098,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         self.fork_choice.write().prune()?;
         let new_finalized_checkpoint = head_state.finalized_checkpoint;
 
-        self.observed_block_producers.prune(
+        self.observed_block_producers.write().prune(
             new_finalized_checkpoint
                 .epoch
                 .start_slot(T::EthSpec::slots_per_epoch()),
```

### beacon_node/beacon_chain/src/block_verification.rs
```diff
@@ -418,6 +418,7 @@ impl<T: BeaconChainTypes> GossipVerifiedBlock<T> {
         // Check that we have not already received a block with a valid signature for this slot.
         if chain
             .observed_block_producers
+            .read()
             .proposer_has_been_observed(&block.message)
             .map_err(|e| BlockError::BeaconChainError(e.into()))?
         {
@@ -472,6 +473,7 @@ impl<T: BeaconChainTypes> GossipVerifiedBlock<T> {
         // have a race-condition when verifying two blocks simultaneously.
         if chain
             .observed_block_producers
+            .write()
             .observe_proposer(&block.message)
             .map_err(|e| BlockError::BeaconChainError(e.into()))?
         {
```

### beacon_node/beacon_chain/src/metrics.rs
```diff
@@ -419,13 +419,15 @@ fn scrape_attestation_observation<T: BeaconChainTypes>(slot_now: Slot, chain: &B
 
     if let Some(count) = chain
         .observed_attesters
+        .read()
         .observed_validator_count(prev_epoch)
     {
         set_gauge_by_usize(&ATTN_OBSERVATION_PREV_EPOCH_ATTESTERS, count);
     }
 
     if let Some(count) = chain
         .observed_aggregators
+        .read()
         .observed_validator_count(prev_epoch)
     {
         set_gauge_by_usize(&ATTN_OBSERVATION_PREV_EPOCH_AGGREGATORS, count);
```

### beacon_node/beacon_chain/src/observed_attestations.rs
```diff
@@ -1,7 +1,6 @@
 //! Provides an `ObservedAttestations` struct which allows us to reject aggregated attestations if
 //! we've already seen the aggregated attestation.
 
-use parking_lot::RwLock;
 use std::collections::HashSet;
 use std::marker::PhantomData;
 use tree_hash::TreeHash;
@@ -116,16 +115,16 @@ impl SlotHashSet {
 /// Stores the roots of `Attestation` objects for some number of `Slots`, so we can determine if
 /// these have previously been seen on the network.
 pub struct ObservedAttestations<E: EthSpec> {
-    lowest_permissible_slot: RwLock<Slot>,
-    sets: RwLock<Vec<SlotHashSet>>,
+    lowest_permissible_slot: Slot,
+    sets: Vec<SlotHashSet>,
     _phantom: PhantomData<E>,
 }
 
 impl<E: EthSpec> Default for ObservedAttestations<E> {
     fn default() -> Self {
         Self {
-            lowest_permissible_slot: RwLock::new(Slot::new(0)),
-            sets: RwLock::new(vec![]),
+            lowest_permissible_slot: Slot::new(0),
+            sets: vec![],
             _phantom: PhantomData,
         }
     }
@@ -136,15 +135,14 @@ impl<E: EthSpec> ObservedAttestations<E> {
     ///
     /// `root` must equal `a.tree_hash_root()`.
     pub fn observe_attestation(
-        &self,
+        &mut self,
         a: &Attestation<E>,
         root_opt: Option<Hash256>,
     ) -> Result<ObserveOutcome, Error> {
         let index = self.get_set_index(a.data.slot)?;
         let root = root_opt.unwrap_or_else(|| a.tree_hash_root());
 
         self.sets
-            .write()
             .get_mut(index)
             .ok_or_else(|| Error::InvalidSetIndex(index))
             .and_then(|set| set.observe_attestation(a, root))
@@ -153,11 +151,10 @@ impl<E: EthSpec> ObservedAttestations<E> {
     /// Check to see if the `root` of `a` is in self.
     ///
     /// `root` must equal `a.tree_hash_root()`.
-    pub fn is_known(&self, a: &Attestation<E>, root: Hash256) -> Result<bool, Error> {
+    pub fn is_known(&mut self, a: &Attestation<E>, root: Hash256) -> Result<bool, Error> {
         let index = self.get_set_index(a.data.slot)?;
 
         self.sets
-            .read()
             .get(index)
             .ok_or_else(|| Error::InvalidSetIndex(index))
             .and_then(|set| set.is_known(a, root))
@@ -172,23 +169,21 @@ impl<E: EthSpec> ObservedAttestations<E> {
 
     /// Removes any attestations with a slot lower than `current_slot` and bars any future
     /// attestations with a slot lower than `current_slot - SLOTS_RETAINED`.
-    pub fn prune(&self, current_slot: Slot) {
+    pub fn prune(&mut self, current_slot: Slot) {
         // Taking advantage of saturating subtraction on `Slot`.
         let lowest_permissible_slot = current_slot - (self.max_capacity() - 1);
 
-        self.sets
-            .write()
-            .retain(|set| set.slot >= lowest_permissible_slot);
+        self.sets.retain(|set| set.slot >= lowest_permissible_slot);
 
-        *self.lowest_permissible_slot.write() = lowest_permissible_slot;
+        self.lowest_permissible_slot = lowest_permissible_slot;
     }
 
     /// Returns the index of `self.set` that matches `slot`.
     ///
     /// If there is no existing set for this slot one will be created. If `self.sets.len() >=
     /// Self::max_capacity()`, the set with the lowest slot will be replaced.
-    fn get_set_index(&self, slot: Slot) -> Result<usize, Error> {
-        let lowest_permissible_slot: Slot = *self.lowest_permissible_slot.read();
+    fn get_set_index(&mut self, slot: Slot) -> Result<usize, Error> {
+        let lowest_permissible_slot = self.lowest_permissible_slot;
 
         if slot < lowest_permissible_slot {
             return Err(Error::SlotTooLow {
@@ -202,15 +197,14 @@ impl<E: EthSpec> ObservedAttestations<E> {
             self.prune(slot)
         }
 
-        let mut sets = self.sets.write();
-
-        if let Some(index) = sets.iter().position(|set| set.slot == slot) {
+        if let Some(index) = self.sets.iter().position(|set| set.slot == slot) {
             return Ok(index);
         }
 
         // To avoid re-allocations, try and determine a rough initial capacity for the new set
         // by obtaining the mean size of all items in earlier epoch.
-        let (count, sum) = sets
+        let (count, sum) = self
+            .sets
             .iter()
             // Only include slots that are less than the given slot in the average. This should
             // generally avoid including recent slots that are still "filling up".
@@ -222,20 +216,21 @@ impl<E: EthSpec> ObservedAttestations<E> {
         // but considering it's approx. 128 * 32 bytes we're not wasting much.
         let initial_capacity = sum.checked_div(count).unwrap_or(128);
 
-        if sets.len() < self.max_capacity() as usize || sets.is_empty() {
-            let index = sets.len();
-            sets.push(SlotHashSet::new(slot, initial_capacity));
+        if self.sets.len() < self.max_capacity() as usize || self.sets.is_empty() {
+            let index = self.sets.len();
+            self.sets.push(SlotHashSet::new(slot, initial_capacity));
             return Ok(index);
         }
 
-        let index = sets
+        let index = self
+            .sets
             .iter()
             .enumerate()
             .min_by_key(|(_i, set)| set.slot)
             .map(|(i, _set)| i)
             .expect("sets cannot be empty due to previous .is_empty() check");
 
-        sets[index] = SlotHashSet::new(slot, initial_capacity);
+        self.sets[index] = SlotHashSet::new(slot, initial_capacity);
 
         Ok(index)
     }
@@ -259,7 +254,7 @@ mod tests {
         a
     }
 
-    fn single_slot_test(store: &ObservedAttestations<E>, slot: Slot) {
+    fn single_slot_test(store: &mut ObservedAttestations<E>, slot: Slot) {
         let attestations = (0..NUM_ELEMENTS as u64)
             .map(|i| get_attestation(slot, i))
             .collect::<Vec<_>>();
@@ -293,46 +288,42 @@ mod tests {
 
     #[test]
     fn single_slot() {
-        let store = ObservedAttestations::default();
+        let mut store = ObservedAttestations::default();
 
-        single_slot_test(&store, Slot::new(0));
+        single_slot_test(&mut store, Slot::new(0));
 
+        assert_eq!(store.sets.len(), 1, "should have a single set stored");
         assert_eq!(
-            store.sets.read().len(),
-            1,
-            "should have a single set stored"
-        );
-        assert_eq!(
-            store.sets.read()[0].len(),
+            store.sets[0].len(),
             NUM_ELEMENTS,
             "set should have NUM_ELEMENTS elements"
         );
     }
 
     #[test]
     fn mulitple_contiguous_slots() {
-        let store = ObservedAttestations::default();
+        let mut store = ObservedAttestations::default();
         let max_cap = store.max_capacity();
 
         for i in 0..max_cap * 3 {
             let slot = Slot::new(i);
 
-            single_slot_test(&store, slot);
+            single_slot_test(&mut store, slot);
 
             /*
              * Ensure that the number of sets is correct.
              */
 
             if i < max_cap {
                 assert_eq!(
-                    store.sets.read().len(),
+                    store.sets.len(),
                     i as usize + 1,
                     "should have a {} sets stored",
                     i + 1
                 );
             } else {
                 assert_eq!(
-                    store.sets.read().len(),
+                    store.sets.len(),
                     max_cap as usize,
                     "should have max_capacity sets stored"
                 );
@@ -342,7 +333,7 @@ mod tests {
              * Ensure that each set contains the correct number of elements.
              */
 
-            for set in &store.sets.read()[..] {
+            for set in &store.sets[..] {
                 assert_eq!(
                     set.len(),
                     NUM_ELEMENTS,
@@ -354,12 +345,7 @@ mod tests {
              *  Ensure that all the sets have the expected slots
              */
 
-            let mut store_slots = store
-                .sets
-                .read()
-                .iter()
-                .map(|set| set.slot)
-                .collect::<Vec<_>>();
+            let mut store_slots = store.sets.iter().map(|set| set.slot).collect::<Vec<_>>();
 
             assert!(
                 store_slots.len() <= store.max_capacity() as usize,
@@ -378,7 +364,7 @@ mod tests {
 
     #[test]
     fn mulitple_non_contiguous_slots() {
-        let store = ObservedAttestations::default();
+        let mut store = ObservedAttestations::default();
         let max_cap = store.max_capacity();
 
         let to_skip = vec![1_u64, 2, 3, 5, 6, 29, 30, 31, 32, 64];
@@ -394,13 +380,13 @@ mod tests {
 
             let slot = Slot::from(i);
 
-            single_slot_test(&store, slot);
+            single_slot_test(&mut store, slot);
 
             /*
              * Ensure that each set contains the correct number of elements.
              */
 
-            for set in &store.sets.read()[..] {
+            for set in &store.sets[..] {
                 assert_eq!(
                     set.len(),
                     NUM_ELEMENTS,
@@ -412,12 +398,7 @@ mod tests {
              *  Ensure that all the sets have the expected slots
              */
 
-            let mut store_slots = store
-                .sets
-                .read()
-                .iter()
-                .map(|set| set.slot)
-                .collect::<Vec<_>>();
+            let mut store_slots = store.sets.iter().map(|set| set.slot).collect::<Vec<_>>();
 
             store_slots.sort_unstable();
 
@@ -426,7 +407,7 @@ mod tests {
                 "store size should not exceed max"
             );
 
-            let lowest = store.lowest_permissible_slot.read().as_u64();
+            let lowest = store.lowest_permissible_slot.as_u64();
             let highest = slot.as_u64();
             let expected_slots = (lowest..=highest)
                 .filter(|i| !to_skip.contains(i))
```

### beacon_node/beacon_chain/src/observed_attesters.rs
```diff
@@ -7,7 +7,6 @@
 //!   the same epoch
 
 use bitvec::vec::BitVec;
-use parking_lot::RwLock;
 use std::collections::{HashMap, HashSet};
 use std::marker::PhantomData;
 use types::{Attestation, Epoch, EthSpec, Unsigned};
@@ -148,16 +147,16 @@ impl Item for EpochHashSet {
 ///
 /// `T` should be set to a `EpochBitfield` or `EpochHashSet`.
 pub struct AutoPruningContainer<T, E: EthSpec> {
-    lowest_permissible_epoch: RwLock<Epoch>,
-    items: RwLock<HashMap<Epoch, T>>,
+    lowest_permissible_epoch: Epoch,
+    items: HashMap<Epoch, T>,
     _phantom: PhantomData<E>,
 }
 
 impl<T, E: EthSpec> Default for AutoPruningContainer<T, E> {
     fn default() -> Self {
         Self {
-            lowest_permissible_epoch: RwLock::new(Epoch::new(0)),
-            items: RwLock::new(HashMap::new()),
+            lowest_permissible_epoch: Epoch::new(0),
+            items: HashMap::new(),
             _phantom: PhantomData,
         }
     }
@@ -172,7 +171,7 @@ impl<T: Item, E: EthSpec> AutoPruningContainer<T, E> {
     /// - `validator_index` is higher than `VALIDATOR_REGISTRY_LIMIT`.
     /// - `a.data.target.slot` is earlier than `self.earliest_permissible_slot`.
     pub fn observe_validator(
-        &self,
+        &mut self,
         a: &Attestation<E>,
         validator_index: usize,
     ) -> Result<bool, Error> {
@@ -182,14 +181,13 @@ impl<T: Item, E: EthSpec> AutoPruningContainer<T, E> {
 
         self.prune(epoch);
 
-        let mut items = self.items.write();
-
-        if let Some(item) = items.get_mut(&epoch) {
+        if let Some(item) = self.items.get_mut(&epoch) {
             Ok(item.insert(validator_index))
         } else {
             // To avoid re-allocations, try and determine a rough initial capacity for the new item
             // by obtaining the mean size of all items in earlier epoch.
-            let (count, sum) = items
+            let (count, sum) = self
+                .items
                 .iter()
                 // Only include epochs that are less than the given slot in the average. This should
                 // generally avoid including recent epochs that are still "filling up".
@@ -201,7 +199,7 @@ impl<T: Item, E: EthSpec> AutoPruningContainer<T, E> {
 
             let mut item = T::with_capacity(initial_capacity);
             item.insert(validator_index);
-            items.insert(epoch, item);
+            self.items.insert(epoch, item);
 
             Ok(false)
         }
@@ -223,7 +221,6 @@ impl<T: Item, E: EthSpec> AutoPruningContainer<T, E> {
 
         let exists = self
             .items
-            .read()
             .get(&a.data.target.epoch)
             .map_or(false, |item| item.contains(validator_index));
 
@@ -233,10 +230,7 @@ impl<T: Item, E: EthSpec> AutoPruningContainer<T, E> {
     /// Returns the number of validators that have been observed at the given `epoch`. Returns
     /// `None` if `self` does not have a cache for that epoch.
     pub fn observed_validator_count(&self, epoch: Epoch) -> Option<usize> {
-        self.items
-            .read()
-            .get(&epoch)
-            .map(|item| item.validator_count())
+        self.items.get(&epoch).map(|item| item.validator_count())
     }
 
     fn sanitize_request(&self, a: &Attestation<E>, validator_index: usize) -> Result<(), Error> {
@@ -245,7 +239,7 @@ impl<T: Item, E: EthSpec> AutoPruningContainer<T, E> {
         }
 
         let epoch = a.data.target.epoch;
-        let lowest_permissible_epoch: Epoch = *self.lowest_permissible_epoch.read();
+        let lowest_permissible_epoch = self.lowest_permissible_epoch;
         if epoch < lowest_permissible_epoch {
             return Err(Error::EpochTooLow {
                 epoch,
@@ -270,14 +264,13 @@ impl<T: Item, E: EthSpec> AutoPruningContainer<T, E> {
     ///
     /// Also sets `self.lowest_permissible_epoch` with relation to `current_epoch` and
     /// `Self::max_capacity`.
-    pub fn prune(&self, current_epoch: Epoch) {
+    pub fn prune(&mut self, current_epoch: Epoch) {
         // Taking advantage of saturating subtraction on `Slot`.
         let lowest_permissible_epoch = current_epoch - (self.max_capacity().saturating_sub(1));
 
-        *self.lowest_permissible_epoch.write() = lowest_permissible_epoch;
+        self.lowest_permissible_epoch = lowest_permissible_epoch;
 
         self.items
-            .write()
             .retain(|epoch, _item| *epoch >= lowest_permissible_epoch);
     }
 }
@@ -301,7 +294,7 @@ mod tests {
                     a
                 }
 
-                fn single_epoch_test(store: &$type<E>, epoch: Epoch) {
+                fn single_epoch_test(store: &mut $type<E>, epoch: Epoch) {
                     let attesters = [0, 1, 2, 3, 5, 6, 7, 18, 22];
                     let a = &get_attestation(epoch);
 
@@ -334,41 +327,37 @@ mod tests {
 
                 #[test]
                 fn single_epoch() {
-                    let store = $type::default();
+                    let mut store = $type::default();
 
-                    single_epoch_test(&store, Epoch::new(0));
+                    single_epoch_test(&mut store, Epoch::new(0));
 
-                    assert_eq!(
-                        store.items.read().len(),
-                        1,
-                        "should have a single bitfield stored"
-                    );
+                    assert_eq!(store.items.len(), 1, "should have a single bitfield stored");
                 }
 
                 #[test]
                 fn mulitple_contiguous_epochs() {
-                    let store = $type::default();
+                    let mut store = $type::default();
                     let max_cap = store.max_capacity();
 
                     for i in 0..max_cap * 3 {
                         let epoch = Epoch::new(i);
 
-                        single_epoch_test(&store, epoch);
+                        single_epoch_test(&mut store, epoch);
 
                         /*
                          * Ensure that the number of sets is correct.
                          */
 
                         if i < max_cap {
                             assert_eq!(
-                                store.items.read().len(),
+                                store.items.len(),
                                 i as usize + 1,
                                 "should have a {} items stored",
                                 i + 1
                             );
                         } else {
                             assert_eq!(
-                                store.items.read().len(),
+                                store.items.len(),
                                 max_cap as usize,
                                 "should have max_capacity items stored"
                             );
@@ -380,7 +369,6 @@ mod tests {
 
                         let mut store_epochs = store
                             .items
-                            .read()
                             .iter()
                             .map(|(epoch, _set)| *epoch)
                             .collect::<Vec<_>>();
@@ -402,7 +390,7 @@ mod tests {
 
                 #[test]
                 fn mulitple_non_contiguous_epochs() {
-                    let store = $type::default();
+                    let mut store = $type::default();
                     let max_cap = store.max_capacity();
 
                     let to_skip = vec![1_u64, 3, 4, 5];
@@ -418,15 +406,14 @@ mod tests {
 
                         let epoch = Epoch::from(i);
 
-                        single_epoch_test(&store, epoch);
+                        single_epoch_test(&mut store, epoch);
 
                         /*
                          *  Ensure that all the sets have the expected slots
                          */
 
                         let mut store_epochs = store
                             .items
-                            .read()
                             .iter()
                             .map(|(epoch, _)| *epoch)
                             .collect::<Vec<_>>();
@@ -438,7 +425,7 @@ mod tests {
                             "store size should not exceed max"
                         );
 
-                        let lowest = store.lowest_permissible_epoch.read().as_u64();
+                        let lowest = store.lowest_permissible_epoch.as_u64();
                         let highest = epoch.as_u64();
                         let expected_epochs = (lowest..=highest)
                             .filter(|i| !to_skip.contains(i))
```

### beacon_node/beacon_chain/src/observed_block_producers.rs
```diff
@@ -1,7 +1,6 @@
 //! Provides the `ObservedBlockProducers` struct which allows for rejecting gossip blocks from
 //! validators that have already produced a block.
 
-use parking_lot::RwLock;
 use std::collections::{HashMap, HashSet};
 use std::marker::PhantomData;
 use types::{BeaconBlock, EthSpec, Slot, Unsigned};
@@ -27,17 +26,17 @@ pub enum Error {
 /// active_validator_count`, however in reality that is more like `slots_since_finality *
 /// known_distinct_shufflings` which is much smaller.
 pub struct ObservedBlockProducers<E: EthSpec> {
-    finalized_slot: RwLock<Slot>,
-    items: RwLock<HashMap<Slot, HashSet<u64>>>,
+    finalized_slot: Slot,
+    items: HashMap<Slot, HashSet<u64>>,
     _phantom: PhantomData<E>,
 }
 
 impl<E: EthSpec> Default for ObservedBlockProducers<E> {
     /// Instantiates `Self` with `finalized_slot == 0`.
     fn default() -> Self {
         Self {
-            finalized_slot: RwLock::new(Slot::new(0)),
-            items: RwLock::new(HashMap::new()),
+            finalized_slot: Slot::new(0),
+            items: HashMap::new(),
             _phantom: PhantomData,
         }
     }
@@ -53,12 +52,11 @@ impl<E: EthSpec> ObservedBlockProducers<E> {
     ///
     /// - `block.proposer_index` is greater than `VALIDATOR_REGISTRY_LIMIT`.
     /// - `block.slot` is equal to or less than the latest pruned `finalized_slot`.
-    pub fn observe_proposer(&self, block: &BeaconBlock<E>) -> Result<bool, Error> {
+    pub fn observe_proposer(&mut self, block: &BeaconBlock<E>) -> Result<bool, Error> {
         self.sanitize_block(block)?;
 
         let did_not_exist = self
             .items
-            .write()
             .entry(block.slot)
             .or_insert_with(|| HashSet::with_capacity(E::SlotsPerEpoch::to_usize()))
             .insert(block.proposer_index);
@@ -79,7 +77,6 @@ impl<E: EthSpec> ObservedBlockProducers<E> {
 
         let exists = self
             .items
-            .read()
             .get(&block.slot)
             .map_or(false, |set| set.contains(&block.proposer_index));
 
@@ -92,7 +89,7 @@ impl<E: EthSpec> ObservedBlockProducers<E> {
             return Err(Error::ValidatorIndexTooHigh(block.proposer_index));
         }
 
-        let finalized_slot = *self.finalized_slot.read();
+        let finalized_slot = self.finalized_slot;
         if finalized_slot > 0 && block.slot <= finalized_slot {
             return Err(Error::FinalizedBlock {
                 slot: block.slot,
@@ -109,15 +106,13 @@ impl<E: EthSpec> ObservedBlockProducers<E> {
     /// equal to or less than `finalized_slot`.
     ///
     /// No-op if `finalized_slot == 0`.
-    pub fn prune(&self, finalized_slot: Slot) {
+    pub fn prune(&mut self, finalized_slot: Slot) {
         if finalized_slot == 0 {
             return;
         }
 
-        *self.finalized_slot.write() = finalized_slot;
-        self.items
-            .write()
-            .retain(|slot, _set| *slot > finalized_slot);
+        self.finalized_slot = finalized_slot;
+        self.items.retain(|slot, _set| *slot > finalized_slot);
     }
 }
 
@@ -137,10 +132,10 @@ mod tests {
 
     #[test]
     fn pruning() {
-        let cache = ObservedBlockProducers::default();
+        let mut cache = ObservedBlockProducers::default();
 
-        assert_eq!(*cache.finalized_slot.read(), 0, "finalized slot is zero");
-        assert_eq!(cache.items.read().len(), 0, "no slots should be present");
+        assert_eq!(cache.finalized_slot, 0, "finalized slot is zero");
+        assert_eq!(cache.items.len(), 0, "no slots should be present");
 
         // Slot 0, proposer 0
         let block_a = &get_block(0, 0);
@@ -155,16 +150,11 @@ mod tests {
          * Preconditions.
          */
 
-        assert_eq!(*cache.finalized_slot.read(), 0, "finalized slot is zero");
-        assert_eq!(
-            cache.items.read().len(),
-            1,
-            "only one slot should be present"
-        );
+        assert_eq!(cache.finalized_slot, 0, "finalized slot is zero");
+        assert_eq!(cache.items.len(), 1, "only one slot should be present");
         assert_eq!(
             cache
                 .items
-                .read()
                 .get(&Slot::new(0))
                 .expect("slot zero should be present")
                 .len(),
@@ -178,16 +168,11 @@ mod tests {
 
         cache.prune(Slot::new(0));
 
-        assert_eq!(*cache.finalized_slot.read(), 0, "finalized slot is zero");
-        assert_eq!(
-            cache.items.read().len(),
-            1,
-            "only one slot should be present"
-        );
+        assert_eq!(cache.finalized_slot, 0, "finalized slot is zero");
+        assert_eq!(cache.items.len(), 1, "only one slot should be present");
         assert_eq!(
             cache
                 .items
-                .read()
                 .get(&Slot::new(0))
                 .expect("slot zero should be present")
                 .len(),
@@ -201,11 +186,11 @@ mod tests {
 
         cache.prune(E::slots_per_epoch().into());
         assert_eq!(
-            *cache.finalized_slot.read(),
+            cache.finalized_slot,
             Slot::from(E::slots_per_epoch()),
             "finalized slot is updated"
         );
-        assert_eq!(cache.items.read().len(), 0, "no items left");
+        assert_eq!(cache.items.len(), 0, "no items left");
 
         /*
          * Check that we can't insert a finalized block
@@ -223,7 +208,7 @@ mod tests {
             "cant insert finalized block"
         );
 
-        assert_eq!(cache.items.read().len(), 0, "block was not added");
+        assert_eq!(cache.items.len(), 0, "block was not added");
 
         /*
          * Check that we _can_ insert a non-finalized block
@@ -240,15 +225,10 @@ mod tests {
             "can insert non-finalized block"
         );
 
-        assert_eq!(
-            cache.items.read().len(),
-            1,
-            "only one slot should be present"
-        );
+        assert_eq!(cache.items.len(), 1, "only one slot should be present");
         assert_eq!(
             cache
                 .items
-                .read()
                 .get(&Slot::new(three_epochs))
                 .expect("the three epochs slot should be present")
                 .len(),
@@ -264,20 +244,15 @@ mod tests {
         cache.prune(two_epochs.into());
 
         assert_eq!(
-            *cache.finalized_slot.read(),
+            cache.finalized_slot,
             Slot::from(two_epochs),
             "finalized slot is updated"
         );
 
-        assert_eq!(
-            cache.items.read().len(),
-            1,
-            "only one slot should be present"
-        );
+        assert_eq!(cache.items.len(), 1, "only one slot should be present");
         assert_eq!(
             cache
                 .items
-                .read()
                 .get(&Slot::new(three_epochs))
                 .expect("the three epochs slot should be present")
                 .len(),
@@ -288,7 +263,7 @@ mod tests {
 
     #[test]
     fn simple_observations() {
-        let cache = ObservedBlockProducers::default();
+        let mut cache = ObservedBlockProducers::default();
 
         // Slot 0, proposer 0
         let block_a = &get_block(0, 0);
@@ -314,16 +289,11 @@ mod tests {
             "observing again indicates true"
         );
 
-        assert_eq!(*cache.finalized_slot.read(), 0, "finalized slot is zero");
-        assert_eq!(
-            cache.items.read().len(),
-            1,
-            "only one slot should be present"
-        );
+        assert_eq!(cache.finalized_slot, 0, "finalized slot is zero");
+        assert_eq!(cache.items.len(), 1, "only one slot should be present");
         assert_eq!(
             cache
                 .items
-                .read()
                 .get(&Slot::new(0))
                 .expect("slot zero should be present")
                 .len(),
@@ -355,12 +325,11 @@ mod tests {
             "observing slot 1 again indicates true"
         );
 
-        assert_eq!(*cache.finalized_slot.read(), 0, "finalized slot is zero");
-        assert_eq!(cache.items.read().len(), 2, "two slots should be present");
+        assert_eq!(cache.finalized_slot, 0, "finalized slot is zero");
+        assert_eq!(cache.items.len(), 2, "two slots should be present");
         assert_eq!(
             cache
                 .items
-                .read()
                 .get(&Slot::new(0))
                 .expect("slot zero should be present")
                 .len(),
@@ -370,7 +339,6 @@ mod tests {
         assert_eq!(
             cache
                 .items
-                .read()
                 .get(&Slot::new(1))
                 .expect("slot zero should be present")
                 .len(),
@@ -402,12 +370,11 @@ mod tests {
             "observing new proposer again indicates true"
         );
 
-        assert_eq!(*cache.finalized_slot.read(), 0, "finalized slot is zero");
-        assert_eq!(cache.items.read().len(), 2, "two slots should be present");
+        assert_eq!(cache.finalized_slot, 0, "finalized slot is zero");
+        assert_eq!(cache.items.len(), 2, "two slots should be present");
         assert_eq!(
             cache
                 .items
-                .read()
                 .get(&Slot::new(0))
                 .expect("slot zero should be present")
                 .len(),
@@ -417,7 +384,6 @@ mod tests {
         assert_eq!(
             cache
                 .items
-                .read()
                 .get(&Slot::new(1))
                 .expect("slot zero should be present")
                 .len(),
```

### beacon_node/beacon_chain/src/observed_operations.rs
```diff
@@ -1,5 +1,4 @@
 use derivative::Derivative;
-use parking_lot::Mutex;
 use smallvec::SmallVec;
 use state_processing::{SigVerifiedOp, VerifyOperation};
 use std::collections::HashSet;
@@ -25,7 +24,7 @@ pub struct ObservedOperations<T: ObservableOperation<E>, E: EthSpec> {
     /// For attester slashings, this is the set of all validators who would be slashed by
     /// previously seen attester slashings, i.e. those validators in the intersection of
     /// `attestation_1.attester_indices` and `attestation_2.attester_indices`.
-    observed_validator_indices: Mutex<HashSet<u64>>,
+    observed_validator_indices: HashSet<u64>,
     _phantom: PhantomData<(T, E)>,
 }
 
@@ -71,12 +70,12 @@ impl<E: EthSpec> ObservableOperation<E> for AttesterSlashing<E> {
 
 impl<T: ObservableOperation<E>, E: EthSpec> ObservedOperations<T, E> {
     pub fn verify_and_observe(
-        &self,
+        &mut self,
         op: T,
         head_state: &BeaconState<E>,
         spec: &ChainSpec,
     ) -> Result<ObservationOutcome<T>, T::Error> {
-        let mut observed_validator_indices = self.observed_validator_indices.lock();
+        let observed_validator_indices = &mut self.observed_validator_indices;
         let new_validator_indices = op.observed_validators();
 
         // If all of the new validator indices have been previously observed, short-circuit
```
