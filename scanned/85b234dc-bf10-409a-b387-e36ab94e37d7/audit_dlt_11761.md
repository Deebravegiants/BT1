# [?] fix(ledger): prevent a potential deadlock in is_solution_limit_reached

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2026-02-09
Source: https://github.com/AleoNet/snarkVM-test/commit/9ba0df7d86303ffe92cfd5682acef8a60575d74c
Type: security-commit

## Details
fix(ledger): prevent a potential deadlock in is_solution_limit_reached

## Patch
### ledger/src/advance.rs
```diff
@@ -289,7 +289,8 @@ impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
                         let prover_address = solution.address();
                         let num_accepted_solutions = accepted_solutions.get(&prover_address).copied().unwrap_or(0);
                         // Check if the prover has reached their solution limit.
-                        if self.is_solution_limit_reached(&prover_address, num_accepted_solutions) {
+                        if self.is_solution_limit_reached_inner(previous_block, &prover_address, num_accepted_solutions)
+                        {
                             return false;
                         }
                         // Check if the solution is valid and update the number of accepted solutions.
```

### ledger/src/check_next_block.rs
```diff
@@ -203,15 +203,20 @@ impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
         block: &Block<N>,
         rng: &mut R,
     ) -> Result<(), CheckBlockError<N>> {
-        let latest_block = self.current_block.read();
+        // Grab lock to the previous block here, to ensure it does not change mid-check.
+        let previous_block = self.current_block.read();
 
         // Ensure, again, that the ledger has not advanced yet. This prevents cryptic errors form appearing during the block check.
-        if block.height() != latest_block.height() + 1 {
-            return Err(CheckBlockError::InvalidHeight { expected: latest_block.height() + 1, actual: block.height() });
+        if block.height() != previous_block.height() + 1 {
+            return Err(CheckBlockError::InvalidHeight {
+                expected: previous_block.height() + 1,
+                actual: block.height(),
+            });
         }
+
         // Also ensure the round is valid, otherwise speculation on transactions will fail with a cryptic error.
-        if block.round() <= latest_block.round() {
-            return Err(CheckBlockError::InvalidRound { new: block.round(), previous: latest_block.round() });
+        if block.round() <= previous_block.round() {
+            return Err(CheckBlockError::InvalidRound { new: block.round(), previous: previous_block.round() });
         }
 
         // Ensure the solutions do not already exist.
@@ -235,7 +240,7 @@ impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
         )?;
 
         // Ensure speculation over the unconfirmed transactions is correct and ensure each transaction is well-formed and unique.
-        let time_since_last_block = block.timestamp().saturating_sub(self.latest_timestamp());
+        let time_since_last_block = block.timestamp().saturating_sub(previous_block.timestamp());
         let ratified_finalize_operations = self.vm.check_speculate(
             state,
             time_since_last_block,
@@ -262,13 +267,13 @@ impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
         // Get the latest epoch hash.
         let latest_epoch_hash = match self.current_epoch_hash.read().as_ref() {
             Some(epoch_hash) => *epoch_hash,
-            None => self.get_epoch_hash(latest_block.height())?,
+            None => self.get_epoch_hash(previous_block.height())?,
         };
 
         // Ensure the block is correct.
         let (expected_existing_solution_ids, expected_existing_transaction_ids) = block
             .verify(
-                &latest_block,
+                &previous_block,
                 self.latest_state_root(),
                 &previous_committee_lookback,
                 &committee_lookback,
@@ -286,7 +291,7 @@ impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
                 let prover_address = solution.address();
                 let num_accepted_solutions = *accepted_solutions.get(&prover_address).unwrap_or(&0);
                 // Check if the prover has reached their solution limit.
-                if self.is_solution_limit_reached(&prover_address, num_accepted_solutions) {
+                if self.is_solution_limit_reached_inner(&previous_block, &prover_address, num_accepted_solutions) {
                     return Err(CheckBlockError::SolutionLimitReached { prover_address });
                 }
                 // Track the already accepted solutions.
```

### ledger/src/is_solution_limit_reached.rs
```diff
@@ -83,12 +83,26 @@ pub fn maximum_allowed_solutions_per_epoch<N: Network>(prover_stake: u64, curren
 
 impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
     /// Returns the number of remaining solutions a prover can submit in the current epoch.
+    ///
+    /// # Locking
+    /// This function may deadlock if called while holding a write lock to the current block.
     pub fn num_remaining_solutions(&self, prover_address: &Address<N>, additional_solutions_in_block: u64) -> u64 {
+        self.num_remaining_solutions_inner(&self.current_block.read(), prover_address, additional_solutions_in_block)
+    }
+
+    /// Internal version of [`Self::num_remaining_solutions`] to be used when already holding a lock to the current block.
+    pub(super) fn num_remaining_solutions_inner(
+        &self,
+        latest_block: &Block<N>,
+        prover_address: &Address<N>,
+        additional_solutions_in_block: u64,
+    ) -> u64 {
         // Fetch the prover's stake.
         let prover_stake = self.get_bonded_amount(prover_address).unwrap_or(0);
 
         // Determine the maximum number of solutions allowed based on this prover's stake.
-        let maximum_allowed_solutions = maximum_allowed_solutions_per_epoch::<N>(prover_stake, self.latest_timestamp());
+        let maximum_allowed_solutions =
+            maximum_allowed_solutions_per_epoch::<N>(prover_stake, latest_block.timestamp());
 
         // Fetch the number of solutions the prover has earned rewards for in the current epoch.
         let prover_num_solutions_in_epoch = *self.epoch_provers_cache.read().get(prover_address).unwrap_or(&0);
@@ -101,9 +115,23 @@ impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
     }
 
     /// Returns `true` if the given prover address has reached their solution limit for the current epoch.
+    ///
+    /// # Locking
+    /// This function may deadlock if called while holding a write lock to the current block.
     pub fn is_solution_limit_reached(&self, prover_address: &Address<N>, additional_solutions_in_block: u64) -> bool {
+        self.is_solution_limit_reached_inner(&self.current_block.read(), prover_address, additional_solutions_in_block)
+    }
+
+    /// Internal version of [`Self::is_solution_limit_reached`] to be used when already holding a lock to the current block.
+    pub(super) fn is_solution_limit_reached_inner(
+        &self,
+        latest_block: &Block<N>,
+        prover_address: &Address<N>,
+        additional_solutions_in_block: u64,
+    ) -> bool {
         // Calculate the number of remaining solutions for the prover.
-        let num_remaining_solutions = self.num_remaining_solutions(prover_address, additional_solutions_in_block);
+        let num_remaining_solutions =
+            self.num_remaining_solutions_inner(latest_block, prover_address, additional_solutions_in_block);
 
         // If the number of remaining solutions is zero, the limit is reached.
         num_remaining_solutions == 0
```
