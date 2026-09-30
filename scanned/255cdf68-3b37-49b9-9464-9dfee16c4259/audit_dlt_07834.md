# [?] Fix deadlock on becaon chain head

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2019-09-11
Source: https://github.com/sigp/lighthouse/commit/5d91d5948115b1f7efc7fd7e403dc5dbbcae715f
Type: security-commit

## Details
Fix deadlock on becaon chain head

## Patch
### beacon_node/beacon_chain/src/beacon_chain.rs
```diff
@@ -8,7 +8,7 @@ use crate::persisted_beacon_chain::{PersistedBeaconChain, BEACON_CHAIN_DB_KEY};
 use lmd_ghost::LmdGhost;
 use operation_pool::DepositInsertStatus;
 use operation_pool::{OperationPool, PersistedOperationPool};
-use parking_lot::{RwLock, RwLockReadGuard};
+use parking_lot::RwLock;
 use slog::{error, info, trace, warn, Logger};
 use slot_clock::SlotClock;
 use ssz::Encode;
@@ -89,35 +89,6 @@ pub enum AttestationProcessingOutcome {
     Invalid(AttestationValidationError),
 }
 
-/// Effectively a `Cow<BeaconState>`, however when it is `Borrowed` it holds a `RwLockReadGuard` (a
-/// read-lock on some read/write-locked state).
-///
-/// Only has a small subset of the functionality of a `std::borrow::Cow`.
-pub enum BeaconStateCow<'a, T: EthSpec> {
-    Borrowed(RwLockReadGuard<'a, CheckPoint<T>>),
-    Owned(BeaconState<T>),
-}
-
-impl<'a, T: EthSpec> BeaconStateCow<'a, T> {
-    pub fn maybe_as_mut_ref(&mut self) -> Option<&mut BeaconState<T>> {
-        match self {
-            BeaconStateCow::Borrowed(_) => None,
-            BeaconStateCow::Owned(ref mut state) => Some(state),
-        }
-    }
-}
-
-impl<'a, T: EthSpec> std::ops::Deref for BeaconStateCow<'a, T> {
-    type Target = BeaconState<T>;
-
-    fn deref(&self) -> &BeaconState<T> {
-        match self {
-            BeaconStateCow::Borrowed(checkpoint) => &checkpoint.beacon_state,
-            BeaconStateCow::Owned(state) => &state,
-        }
-    }
-}
-
 pub trait BeaconChainTypes: Send + Sync + 'static {
     type Store: store::Store;
     type SlotClock: slot_clock::SlotClock;
@@ -338,13 +309,11 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
     /// - As this iterator starts at the `head` of the chain (viz., the best block), the first slot
     ///     returned may be earlier than the wall-clock slot.
     pub fn rev_iter_block_roots(&self) -> ReverseBlockRootIterator<T::EthSpec, T::Store> {
-        let state = &self.head().beacon_state;
-        let block_root = self.head().beacon_block_root;
-        let block_slot = state.slot;
+        let head = self.head();
 
-        let iter = BlockRootsIterator::owned(self.store.clone(), state.clone());
+        let iter = BlockRootsIterator::owned(self.store.clone(), head.beacon_state);
 
-        ReverseBlockRootIterator::new((block_root, block_slot), iter)
+        ReverseBlockRootIterator::new((head.beacon_block_root, head.beacon_block.slot), iter)
     }
 
     /// Iterates across all `(state_root, slot)` pairs from the head of the chain (inclusive) to
@@ -357,13 +326,12 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
     /// - As this iterator starts at the `head` of the chain (viz., the best block), the first slot
     ///     returned may be earlier than the wall-clock slot.
     pub fn rev_iter_state_roots(&self) -> ReverseStateRootIterator<T::EthSpec, T::Store> {
-        let state = &self.head().beacon_state;
-        let state_root = self.head().beacon_state_root;
-        let state_slot = state.slot;
+        let head = self.head();
+        let slot = head.beacon_state.slot;
 
-        let iter = StateRootsIterator::owned(self.store.clone(), state.clone());
+        let iter = StateRootsIterator::owned(self.store.clone(), head.beacon_state);
 
-        ReverseStateRootIterator::new((state_root, state_slot), iter)
+        ReverseStateRootIterator::new((head.beacon_state_root, slot), iter)
     }
 
     /// Returns the block at the given root, if any.
@@ -378,32 +346,25 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         Ok(self.store.get(block_root)?)
     }
 
-    /// Returns a read-lock guarded `CheckPoint` struct for reading the head (as chosen by the
-    /// fork-choice rule).
+    /// Returns a `Checkpoint` representing the head block and state. Contains the "best block";
+    /// the head of the canonical `BeaconChain`.
     ///
     /// It is important to note that the `beacon_state` returned may not match the present slot. It
     /// is the state as it was when the head block was received, which could be some slots prior to
     /// now.
-    pub fn head<'a>(&'a self) -> RwLockReadGuard<'a, CheckPoint<T::EthSpec>> {
-        self.canonical_head.read()
+    pub fn head(&self) -> CheckPoint<T::EthSpec> {
+        self.canonical_head.read().clone()
     }
 
     /// Returns the `BeaconState` at the given slot.
     ///
-    /// May return:
-    ///
-    ///  - A new state loaded from the database (for states prior to the head)
-    ///  - A reference to the head state (note: this keeps a read lock on the head, try to use
-    ///  sparingly).
-    ///  - The head state, but with skipped slots (for states later than the head).
-    ///
     ///  Returns `None` when the state is not found in the database or there is an error skipping
     ///  to a future state.
-    pub fn state_at_slot(&self, slot: Slot) -> Result<BeaconStateCow<T::EthSpec>, Error> {
-        let head_state = &self.head().beacon_state;
+    pub fn state_at_slot(&self, slot: Slot) -> Result<BeaconState<T::EthSpec>, Error> {
+        let head_state = self.head().beacon_state;
 
         if slot == head_state.slot {
-            Ok(BeaconStateCow::Borrowed(self.head()))
+            Ok(head_state)
         } else if slot > head_state.slot {
             let head_state_slot = head_state.slot;
             let mut state = head_state.clone();
@@ -423,19 +384,18 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
                     }
                 };
             }
-            Ok(BeaconStateCow::Owned(state))
+            Ok(state)
         } else {
             let state_root = self
                 .rev_iter_state_roots()
                 .find(|(_root, s)| *s == slot)
                 .map(|(root, _slot)| root)
                 .ok_or_else(|| Error::NoStateForSlot(slot))?;
 
-            Ok(BeaconStateCow::Owned(
-                self.store
-                    .get(&state_root)?
-                    .ok_or_else(|| Error::NoStateForSlot(slot))?,
-            ))
+            Ok(self
+                .store
+                .get(&state_root)?
+                .ok_or_else(|| Error::NoStateForSlot(slot))?)
         }
     }
 
@@ -447,7 +407,7 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
     ///
     ///  Returns `None` when there is an error skipping to a future state or the slot clock cannot
     ///  be read.
-    pub fn state_now(&self) -> Result<BeaconStateCow<T::EthSpec>, Error> {
+    pub fn wall_clock_state(&self) -> Result<BeaconState<T::EthSpec>, Error> {
         self.state_at_slot(self.slot()?)
     }
 
@@ -499,14 +459,12 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         let head_state = &self.head().beacon_state;
 
         let mut state = if epoch(slot) == epoch(head_state.slot) {
-            BeaconStateCow::Borrowed(self.head())
+            self.head().beacon_state.clone()
         } else {
             self.state_at_slot(slot)?
         };
 
-        if let Some(state) = state.maybe_as_mut_ref() {
-            state.build_committee_cache(RelativeEpoch::Current, &self.spec)?;
-        }
+        state.build_committee_cache(RelativeEpoch::Current, &self.spec)?;
 
         if epoch(state.slot) != epoch(slot) {
             return Err(Error::InvariantViolated(format!(
@@ -534,14 +492,12 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         let head_state = &self.head().beacon_state;
 
         let mut state = if epoch == as_epoch(head_state.slot) {
-            BeaconStateCow::Borrowed(self.head())
+            self.head().beacon_state.clone()
         } else {
             self.state_at_slot(epoch.start_slot(T::EthSpec::slots_per_epoch()))?
         };
 
-        if let Some(state) = state.maybe_as_mut_ref() {
-            state.build_committee_cache(RelativeEpoch::Current, &self.spec)?;
-        }
+        state.build_committee_cache(RelativeEpoch::Current, &self.spec)?;
 
         if as_epoch(state.slot) != epoch {
             return Err(Error::InvariantViolated(format!(
@@ -569,11 +525,14 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         slot: Slot,
     ) -> Result<AttestationData, Error> {
         let state = self.state_at_slot(slot)?;
+        let head = self.head();
 
-        let head_block_root = self.head().beacon_block_root;
-        let head_block_slot = self.head().beacon_block.slot;
-
-        self.produce_attestation_data_for_block(shard, head_block_root, head_block_slot, &*state)
+        self.produce_attestation_data_for_block(
+            shard,
+            head.beacon_block_root,
+            head.beacon_block.slot,
+            &state,
+        )
     }
 
     /// Produce an `AttestationData` that attests to the chain denoted by `block_root` and `state`.
@@ -900,10 +859,8 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
 
     /// Accept some exit and queue it for inclusion in an appropriate block.
     pub fn process_voluntary_exit(&self, exit: VoluntaryExit) -> Result<(), ExitValidationError> {
-        match self.state_now() {
-            Ok(state) => self
-                .op_pool
-                .insert_voluntary_exit(exit, &*state, &self.spec),
+        match self.wall_clock_state() {
+            Ok(state) => self.op_pool.insert_voluntary_exit(exit, &state, &self.spec),
             Err(e) => {
                 error!(
                     &self.log,
@@ -918,8 +875,8 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
 
     /// Accept some transfer and queue it for inclusion in an appropriate block.
     pub fn process_transfer(&self, transfer: Transfer) -> Result<(), TransferValidationError> {
-        match self.state_now() {
-            Ok(state) => self.op_pool.insert_transfer(transfer, &*state, &self.spec),
+        match self.wall_clock_state() {
+            Ok(state) => self.op_pool.insert_transfer(transfer, &state, &self.spec),
             Err(e) => {
                 error!(
                     &self.log,
@@ -937,10 +894,10 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         &self,
         proposer_slashing: ProposerSlashing,
     ) -> Result<(), ProposerSlashingValidationError> {
-        match self.state_now() {
+        match self.wall_clock_state() {
             Ok(state) => {
                 self.op_pool
-                    .insert_proposer_slashing(proposer_slashing, &*state, &self.spec)
+                    .insert_proposer_slashing(proposer_slashing, &state, &self.spec)
             }
             Err(e) => {
                 error!(
@@ -959,10 +916,10 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         &self,
         attester_slashing: AttesterSlashing<T::EthSpec>,
     ) -> Result<(), AttesterSlashingValidationError> {
-        match self.state_now() {
+        match self.wall_clock_state() {
             Ok(state) => {
                 self.op_pool
-                    .insert_attester_slashing(attester_slashing, &*state, &self.spec)
+                    .insert_attester_slashing(attester_slashing, &state, &self.spec)
             }
             Err(e) => {
                 error!(
```
