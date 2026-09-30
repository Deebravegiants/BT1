# [?] Merge pull request #3182 from damons/fix/ledger-current-block-rwlock-deadlock-v4.5.0

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2026-03-12
Source: https://github.com/AleoNet/snarkVM-test/commit/eb6d42f2bd7307ac3d3c51d4014a7da28abe6250
Type: security-commit

## Details
Merge pull request #3182 from damons/fix/ledger-current-block-rwlock-deadlock-v4.5.0

Backport ledger current_block deadlock fix to mainnet

## Patch
### ledger/src/check_next_block.rs
```diff
@@ -202,6 +202,7 @@ impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
         rng: &mut R,
     ) -> Result<(), CheckBlockError<N>> {
         let latest_block = self.current_block.read();
+        let latest_block_timestamp = latest_block.timestamp();
 
         // Ensure, again, that the ledger has not advanced yet. This prevents cryptic errors form appearing during the block check.
         if block.height() != latest_block.height() + 1 {
@@ -229,7 +230,7 @@ impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
         )?;
 
         // Ensure speculation over the unconfirmed transactions is correct and ensure each transaction is well-formed and unique.
-        let time_since_last_block = block.timestamp().saturating_sub(self.latest_timestamp());
+        let time_since_last_block = block.timestamp().saturating_sub(latest_block_timestamp);
         let ratified_finalize_operations = self.vm.check_speculate(
             state,
             time_since_last_block,
@@ -274,7 +275,11 @@ impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
                 let prover_address = solution.address();
                 let num_accepted_solutions = *accepted_solutions.get(&prover_address).unwrap_or(&0);
                 // Check if the prover has reached their solution limit.
-                if self.is_solution_limit_reached(&prover_address, num_accepted_solutions) {
+                if self.is_solution_limit_reached_at_timestamp(
+                    &prover_address,
+                    num_accepted_solutions,
+                    latest_block_timestamp,
+                ) {
                     return Err(CheckBlockError::SolutionLimitReached { prover_address });
                 }
                 // Track the already accepted solutions.
```

### ledger/src/is_solution_limit_reached.rs
```diff
@@ -82,13 +82,19 @@ pub fn maximum_allowed_solutions_per_epoch<N: Network>(prover_stake: u64, curren
 }
 
 impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
-    /// Returns the number of remaining solutions a prover can submit in the current epoch.
-    pub fn num_remaining_solutions(&self, prover_address: &Address<N>, additional_solutions_in_block: u64) -> u64 {
+    /// Returns the number of remaining solutions a prover can submit in the current epoch,
+    /// using the provided ledger timestamp instead of re-reading the current block.
+    pub(crate) fn num_remaining_solutions_at_timestamp(
+        &self,
+        prover_address: &Address<N>,
+        additional_solutions_in_block: u64,
+        current_time: i64,
+    ) -> u64 {
         // Fetch the prover's stake.
         let prover_stake = self.get_bonded_amount(prover_address).unwrap_or(0);
 
         // Determine the maximum number of solutions allowed based on this prover's stake.
-        let maximum_allowed_solutions = maximum_allowed_solutions_per_epoch::<N>(prover_stake, self.latest_timestamp());
+        let maximum_allowed_solutions = maximum_allowed_solutions_per_epoch::<N>(prover_stake, current_time);
 
         // Fetch the number of solutions the prover has earned rewards for in the current epoch.
         let prover_num_solutions_in_epoch = *self.epoch_provers_cache.read().get(prover_address).unwrap_or(&0);
@@ -100,19 +106,41 @@ impl<N: Network, C: ConsensusStorage<N>> Ledger<N, C> {
         maximum_allowed_solutions.saturating_sub(num_solutions)
     }
 
+    /// Returns the number of remaining solutions a prover can submit in the current epoch.
+    pub fn num_remaining_solutions(&self, prover_address: &Address<N>, additional_solutions_in_block: u64) -> u64 {
+        self.num_remaining_solutions_at_timestamp(
+            prover_address,
+            additional_solutions_in_block,
+            self.latest_timestamp(),
+        )
+    }
+
+    /// Returns `true` if the given prover address has reached their solution limit for the current epoch,
+    /// using the provided ledger timestamp instead of re-reading the current block.
+    pub(crate) fn is_solution_limit_reached_at_timestamp(
+        &self,
+        prover_address: &Address<N>,
+        additional_solutions_in_block: u64,
+        current_time: i64,
+    ) -> bool {
+        self.num_remaining_solutions_at_timestamp(prover_address, additional_solutions_in_block, current_time) == 0
+    }
+
     /// Returns `true` if the given prover address has reached their solution limit for the current epoch.
     pub fn is_solution_limit_reached(&self, prover_address: &Address<N>, additional_solutions_in_block: u64) -> bool {
-        // Calculate the number of remaining solutions for the prover.
-        let num_remaining_solutions = self.num_remaining_solutions(prover_address, additional_solutions_in_block);
-
-        // If the number of remaining solutions is zero, the limit is reached.
-        num_remaining_solutions == 0
+        self.is_solution_limit_reached_at_timestamp(
+            prover_address,
+            additional_solutions_in_block,
+            self.latest_timestamp(),
+        )
     }
 }
 
 #[cfg(test)]
 mod tests {
     use super::*;
+    use crate::test_helpers::{CurrentLedger, LedgerType};
+    use std::{thread, time::Duration};
 
     type CurrentNetwork = console::network::MainnetV0;
 
@@ -198,4 +226,37 @@ mod tests {
             );
         }
     }
+
+    #[test]
+    fn test_solution_limit_helper_avoids_current_block_reentry_with_pending_writer() {
+        let rng = &mut TestRng::default();
+
+        let private_key = PrivateKey::<CurrentNetwork>::new(rng).unwrap();
+        let validator_address = Address::try_from(&private_key).unwrap();
+        let store = ConsensusStore::<CurrentNetwork, LedgerType>::open(StorageMode::new_test(None)).unwrap();
+        let genesis = VM::from(store).unwrap().genesis_beacon(&private_key, rng).unwrap();
+        let ledger = CurrentLedger::load(genesis, StorageMode::new_test(None)).unwrap();
+
+        let next_block =
+            ledger.prepare_advance_to_next_beacon_block(&private_key, vec![], vec![], vec![], rng).unwrap();
+        let expected = ledger.num_remaining_solutions(&validator_address, 0);
+
+        // Mimic check_next_block() holding a read guard while a writer queues behind it.
+        let latest_block = ledger.current_block.read();
+        let latest_timestamp = latest_block.timestamp();
+
+        let ledger_clone = ledger.clone();
+        let next_block_clone = next_block.clone();
+        let writer = thread::spawn(move || ledger_clone.advance_to_next_block(&next_block_clone));
+
+        thread::sleep(Duration::from_millis(50));
+        assert!(!writer.is_finished(), "advance_to_next_block should be waiting on current_block.write()");
+
+        let actual = ledger.num_remaining_solutions_at_timestamp(&validator_address, 0, latest_timestamp);
+        assert_eq!(actual, expected);
+        assert_eq!(ledger.is_solution_limit_reached_at_timestamp(&validator_address, 0, latest_timestamp), actual == 0);
+
+        drop(latest_block);
+        writer.join().unwrap().unwrap();
+    }
 }
```
