# [?] Avoid over-/underflow error in coin_select

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoindevkit/bdk
Published: 2021-04-01
Source: https://github.com/bitcoindevkit/bdk/commit/e5ecc7f5410aea9d7a108a46d01c7a2fa0822bb7
Type: security-commit

## Details
Avoid over-/underflow error in coin_select

Adds fix for edge-cases involving small UTXOs (where value < fee) where the coin_select calculation would panic with overflow/underflow errors.
Bitcoin is limited to 21*(10^6), so any Bitcoin amount fits into i64.

## Patch
### CHANGELOG.md
```diff
@@ -24,6 +24,9 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 - Added `get_address(AddressIndex::Reset(u32))` which returns a derived address for a specified descriptor index and resets current index to the given value
 - Added `get_psbt_input` to create the corresponding psbt input for a local utxo.
 
+#### Fixed
+- Fixed `coin_select` calculation for UTXOs where `value < fee` that caused over-/underflow errors.
+
 ## [v0.5.1] - [v0.5.0]
 
 ### Misc
```

### src/wallet/coin_selection.rs
```diff
@@ -91,6 +91,7 @@ use rand::seq::SliceRandom;
 use rand::thread_rng;
 #[cfg(test)]
 use rand::{rngs::StdRng, SeedableRng};
+use std::convert::TryInto;
 
 /// Default coin selection algorithm used by [`TxBuilder`](super::tx_builder::TxBuilder) if not
 /// overridden
@@ -303,32 +304,39 @@ impl<D: Database> CoinSelectionAlgorithm<D> for BranchAndBoundCoinSelection {
             .collect();
 
         // Mapping every (UTXO, usize) to an output group.
-        // Filtering UTXOs with an effective_value < 0, as the fee paid for
-        // adding them is more than their value
         let optional_utxos: Vec<OutputGroup> = optional_utxos
             .into_iter()
             .map(|u| OutputGroup::new(u, fee_rate))
-            .filter(|u| u.effective_value > 0)
             .collect();
 
         let curr_value = required_utxos
             .iter()
-            .fold(0, |acc, x| acc + x.effective_value as u64);
+            .fold(0, |acc, x| acc + x.effective_value);
 
         let curr_available_value = optional_utxos
             .iter()
-            .fold(0, |acc, x| acc + x.effective_value as u64);
+            .fold(0, |acc, x| acc + x.effective_value);
 
         let actual_target = fee_amount.ceil() as u64 + amount_needed;
         let cost_of_change = self.size_of_change as f32 * fee_rate.as_sat_vb();
 
-        if curr_available_value + curr_value < actual_target {
+        let expected = (curr_available_value + curr_value)
+            .try_into()
+            .map_err(|_| {
+                Error::Generic("Sum of UTXO spendable values does not fit into u64".to_string())
+            })?;
+
+        if expected < actual_target {
             return Err(Error::InsufficientFunds {
                 needed: actual_target,
-                available: curr_available_value + curr_value,
+                available: expected,
             });
         }
 
+        let actual_target = actual_target
+            .try_into()
+            .expect("Bitcoin amount to fit into i64");
+
         Ok(self
             .bnb(
                 required_utxos.clone(),
@@ -359,9 +367,9 @@ impl BranchAndBoundCoinSelection {
         &self,
         required_utxos: Vec<OutputGroup>,
         mut optional_utxos: Vec<OutputGroup>,
-        mut curr_value: u64,
-        mut curr_available_value: u64,
-        actual_target: u64,
+        mut curr_value: i64,
+        mut curr_available_value: i64,
+        actual_target: i64,
         fee_amount: f32,
         cost_of_change: f32,
     ) -> Result<CoinSelectionResult, Error> {
@@ -387,7 +395,7 @@ impl BranchAndBoundCoinSelection {
             // or the selected value is out of range.
             // Go back and try other branch
             if curr_value + curr_available_value < actual_target
-                || curr_value > actual_target + cost_of_change as u64
+                || curr_value > actual_target + cost_of_change as i64
             {
                 backtrack = true;
             } else if curr_value >= actual_target {
@@ -413,8 +421,7 @@ impl BranchAndBoundCoinSelection {
                 // Walk backwards to find the last included UTXO that still needs to have its omission branch traversed.
                 while let Some(false) = current_selection.last() {
                     current_selection.pop();
-                    curr_available_value +=
-                        optional_utxos[current_selection.len()].effective_value as u64;
+                    curr_available_value += optional_utxos[current_selection.len()].effective_value;
                 }
 
                 if current_selection.last_mut().is_none() {
@@ -432,17 +439,17 @@ impl BranchAndBoundCoinSelection {
                 }
 
                 let utxo = &optional_utxos[current_selection.len() - 1];
-                curr_value -= utxo.effective_value as u64;
+                curr_value -= utxo.effective_value;
             } else {
                 // Moving forwards, continuing down this branch
                 let utxo = &optional_utxos[current_selection.len()];
 
                 // Remove this utxo from the curr_available_value utxo amount
-                curr_available_value -= utxo.effective_value as u64;
+                curr_available_value -= utxo.effective_value;
 
                 // Inclusion branch first (Largest First Exploration)
                 current_selection.push(true);
-                curr_value += utxo.effective_value as u64;
+                curr_value += utxo.effective_value;
             }
         }
 
@@ -469,8 +476,8 @@ impl BranchAndBoundCoinSelection {
         &self,
         required_utxos: Vec<OutputGroup>,
         mut optional_utxos: Vec<OutputGroup>,
-        curr_value: u64,
-        actual_target: u64,
+        curr_value: i64,
+        actual_target: i64,
         fee_amount: f32,
     ) -> CoinSelectionResult {
         #[cfg(not(test))]
@@ -488,7 +495,7 @@ impl BranchAndBoundCoinSelection {
                 if *curr_value >= actual_target {
                     None
                 } else {
-                    *curr_value += utxo.effective_value as u64;
+                    *curr_value += utxo.effective_value;
                     Some(utxo)
                 }
             })
@@ -532,13 +539,15 @@ mod test {
 
     const P2WPKH_WITNESS_SIZE: usize = 73 + 33 + 2;
 
+    const FEE_AMOUNT: f32 = 50.0;
+
     fn get_test_utxos() -> Vec<WeightedUtxo> {
         vec![
             WeightedUtxo {
                 satisfaction_weight: P2WPKH_WITNESS_SIZE,
                 utxo: Utxo::Local(LocalUtxo {
                     outpoint: OutPoint::from_str(
-                        "ebd9813ecebc57ff8f30797de7c205e3c7498ca950ea4341ee51a685ff2fa30a:0",
+                        "0000000000000000000000000000000000000000000000000000000000000000:0",
                     )
                     .unwrap(),
                     txout: TxOut {
@@ -552,7 +561,21 @@ mod test {
                 satisfaction_weight: P2WPKH_WITNESS_SIZE,
                 utxo: Utxo::Local(LocalUtxo {
                     outpoint: OutPoint::from_str(
-                        "65d92ddff6b6dc72c89624a6491997714b90f6004f928d875bc0fd53f264fa85:0",
+                        "0000000000000000000000000000000000000000000000000000000000000001:0",
+                    )
+                    .unwrap(),
+                    txout: TxOut {
+                        value: FEE_AMOUNT as u64 - 40,
+                        script_pubkey: Script::new(),
+                    },
+                    keychain: KeychainKind::External,
+                }),
+            },
+            WeightedUtxo {
+                satisfaction_weight: P2WPKH_WITNESS_SIZE,
+                utxo: Utxo::Local(LocalUtxo {
+                    outpoint: OutPoint::from_str(
+                        "0000000000000000000000000000000000000000000000000000000000000002:0",
                     )
                     .unwrap(),
                     txout: TxOut {
@@ -629,9 +652,9 @@ mod test {
             )
             .unwrap();
 
-        assert_eq!(result.selected.len(), 2);
-        assert_eq!(result.selected_amount(), 300_000);
-        assert_eq!(result.fee_amount, 186.0);
+        assert_eq!(result.selected.len(), 3);
+        assert_eq!(result.selected_amount(), 300_010);
+        assert_eq!(result.fee_amount, 254.0);
     }
 
     #[test]
@@ -650,9 +673,9 @@ mod test {
             )
             .unwrap();
 
-        assert_eq!(result.selected.len(), 2);
-        assert_eq!(result.selected_amount(), 300_000);
-        assert_eq!(result.fee_amount, 186.0);
+        assert_eq!(result.selected.len(), 3);
+        assert_eq!(result.selected_amount(), 300_010);
+        assert_eq!(result.fee_amount, 254.0);
     }
 
     #[test]
@@ -748,13 +771,34 @@ mod test {
                 utxos,
                 FeeRate::from_sat_per_vb(1.0),
                 20_000,
-                50.0,
+                FEE_AMOUNT,
             )
             .unwrap();
 
-        assert_eq!(result.selected.len(), 2);
-        assert_eq!(result.selected_amount(), 300_000);
-        assert_eq!(result.fee_amount, 186.0);
+        assert_eq!(result.selected.len(), 3);
+        assert_eq!(result.selected_amount(), 300_010);
+        assert_eq!(result.fee_amount, 254.0);
+    }
+
+    #[test]
+    fn test_bnb_coin_selection_optional_are_enough() {
+        let utxos = get_test_utxos();
+        let database = MemoryDatabase::default();
+
+        let result = BranchAndBoundCoinSelection::default()
+            .coin_select(
+                &database,
+                vec![],
+                utxos,
+                FeeRate::from_sat_per_vb(1.0),
+                299756,
+                FEE_AMOUNT,
+            )
+            .unwrap();
+
+        assert_eq!(result.selected.len(), 3);
+        assert_eq!(result.selected_amount(), 300010);
+        assert_eq!(result.fee_amount, 254.0);
     }
 
     #[test]
@@ -848,9 +892,7 @@ mod test {
             .map(|u| OutputGroup::new(u, fee_rate))
             .collect();
 
-        let curr_available_value = utxos
-            .iter()
-            .fold(0, |acc, x| acc + x.effective_value as u64);
+        let curr_available_value = utxos.iter().fold(0, |acc, x| acc + x.effective_value);
 
         let size_of_change = 31;
         let cost_of_change = size_of_change as f32 * fee_rate.as_sat_vb();
@@ -876,9 +918,7 @@ mod test {
             .map(|u| OutputGroup::new(u, fee_rate))
             .collect();
 
-        let curr_available_value = utxos
-            .iter()
-            .fold(0, |acc, x| acc + x.effective_value as u64);
+        let curr_available_value = utxos.iter().fold(0, |acc, x| acc + x.effective_value);
 
         let size_of_change = 31;
         let cost_of_change = size_of_change as f32 * fee_rate.as_sat_vb();
@@ -911,13 +951,11 @@ mod test {
 
         let curr_value = 0;
 
-        let curr_available_value = utxos
-            .iter()
-            .fold(0, |acc, x| acc + x.effective_value as u64);
+        let curr_available_value = utxos.iter().fold(0, |acc, x| acc + x.effective_value);
 
         // 2*(value of 1 utxo)  - 2*(1 utxo fees with 1.0sat/vbyte fee rate) -
         // cost_of_change + 5.
-        let target_amount = 2 * 50_000 - 2 * 67 - cost_of_change.ceil() as u64 + 5;
+        let target_amount = 2 * 50_000 - 2 * 67 - cost_of_change.ceil() as i64 + 5;
 
         let result = BranchAndBoundCoinSelection::new(size_of_change)
             .bnb(
@@ -951,10 +989,10 @@ mod test {
 
             let curr_available_value = optional_utxos
                 .iter()
-                .fold(0, |acc, x| acc + x.effective_value as u64);
+                .fold(0, |acc, x| acc + x.effective_value);
 
-            let target_amount = optional_utxos[3].effective_value as u64
-                + optional_utxos[23].effective_value as u64;
+            let target_amount =
+                optional_utxos[3].effective_value + optional_utxos[23].effective_value;
 
             let result = BranchAndBoundCoinSelection::new(0)
                 .bnb(
@@ -967,7 +1005,7 @@ mod test {
                     0.0,
                 )
                 .unwrap();
-            assert_eq!(result.selected_amount(), target_amount);
+            assert_eq!(result.selected_amount(), target_amount as u64);
         }
     }
 
@@ -988,7 +1026,7 @@ mod test {
             vec![],
             utxos,
             0,
-            target_amount,
+            target_amount as i64,
             50.0,
         );
 
```
