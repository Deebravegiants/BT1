# [?] fix: don't panic when trying to spend too much BTC  (#3693)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2023-07-20
Source: https://github.com/chainflip-io/chainflip-backend/commit/71264bf2ff0db9e4032fb2bbc901752cff438e4a
Type: security-commit

## Details
fix: don't panic when trying to spend too much BTC  (#3693)

Co-authored-by: Daniel <daniel@chainflip.io>
Co-authored-by: dandanlen <3168260+dandanlen@users.noreply.github.com>

## Patch
### state-chain/chains/src/btc/utxo_selection.rs
```diff
@@ -41,7 +41,7 @@ pub fn select_utxos_from_pool<UTXO: GetUtxoAmount + Clone>(
 				skipped_utxos.push(current_smallest_utxo.clone());
 			}
 		} else {
-			break
+			return None
 		}
 	}
 
@@ -124,14 +124,11 @@ fn test_utxo_selection() {
 	// max amount that can be spent with the given utxos.
 	assert_eq!(
 		select_utxos_from_pool(&mut available_utxos.clone(), FEE_PER_UTXO, 2485),
-		Some((all_selected_utxos.clone(), 2485))
-	);
-	// entering the amount greater than the max spendable amount will
-	// cause the function to select all available utxos
-	assert_eq!(
-		select_utxos_from_pool(&mut available_utxos.clone(), FEE_PER_UTXO, 100000),
 		Some((all_selected_utxos, 2485))
 	);
+	// entering the amount greater than the max spendable amount will
+	// cause the function to return no utxos
+	assert_eq!(select_utxos_from_pool(&mut available_utxos.clone(), FEE_PER_UTXO, 100000), None);
 
 	// choosing the fee to spend the input utxo as greater than the amounts in the 2 smallest utxos
 	// will cause the algorithm to skip the selection of those 2 utxos and adding it to the list of
```

### state-chain/pallets/cf-environment/src/lib.rs
```diff
@@ -553,15 +553,19 @@ impl<T: Config> Pallet<T> {
 				})
 			},
 			UtxoSelectionType::Some { output_amount, number_of_outputs } =>
-				BitcoinAvailableUtxos::<T>::mutate(|available_utxos| {
+				BitcoinAvailableUtxos::<T>::try_mutate(|available_utxos| {
 					select_utxos_from_pool(
 						available_utxos,
 						fee_per_input_utxo,
 						output_amount +
 							number_of_outputs * fee_per_output_utxo +
 							min_fee_required_per_tx,
 					)
+					.ok_or_else(|| {
+						log::error!("Unable to select desired amount from available utxos.");
+					})
 				})
+				.ok()
 				.map(|(selected_utxos, total_input_spendable_amount)| {
 					(
 						selected_utxos,
```

### state-chain/pallets/cf-environment/src/tests.rs
```diff
@@ -116,6 +116,24 @@ fn test_btc_utxo_selection() {
 				.unwrap(),
 			(vec![utxo(5000000), utxo(120080),], 5116060)
 		);
+
+		// add some more utxos to the list
+		Environment::add_bitcoin_utxo_to_list(5000, Default::default(), SCRIPT_PUBKEY);
+		Environment::add_bitcoin_utxo_to_list(15000, Default::default(), SCRIPT_PUBKEY);
+
+		// request a larger amount than what is available
+		assert!(Environment::select_and_take_bitcoin_utxos(UtxoSelectionType::Some {
+			output_amount: 20100,
+			number_of_outputs: 1
+		})
+		.is_none());
+
+		// Ensure the previous failure didn't wipe the utxo list
+		assert_eq!(
+			Environment::select_and_take_bitcoin_utxos(UtxoSelectionType::SelectAllForRotation)
+				.unwrap(),
+			(vec![utxo(5000), utxo(15000),], 15980)
+		);
 	});
 }
 
```
