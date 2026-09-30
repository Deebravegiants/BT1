# [?] Merge pull request #929 from chainflip-io/fix/broadcast-and-offline-crash-loop

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2021-12-06
Source: https://github.com/chainflip-io/chainflip-backend/commit/018633333ce85b4e18b01e935ad6493d5b82afbb
Type: security-commit

## Details
Merge pull request #929 from chainflip-io/fix/broadcast-and-offline-crash-loop

Broadcast and Offline crash loop

## Patch
### state-chain/pallets/cf-broadcast/src/lib.rs
```diff
@@ -480,28 +480,41 @@ impl<T: Config<I>, I: 'static> Pallet<T, I> {
 		// Select a signer for this broadcast.
 		let nominated_signer = T::SignerNomination::nomination_with_seed(attempt_id);
 
-		AwaitingTransactionSignature::<T, I>::insert(
-			attempt_id,
-			TransactionSigningAttempt::<T, I> {
+		// Check if there is an nominated signer
+		if let Some(nominated_signer) = nominated_signer {
+			AwaitingTransactionSignature::<T, I>::insert(
+				attempt_id,
+				TransactionSigningAttempt::<T, I> {
+					broadcast_id,
+					attempt_count,
+					unsigned_tx: unsigned_tx.clone(),
+					nominee: nominated_signer.clone(),
+				},
+			);
+
+			// Schedule expiry.
+			let expiry_block = frame_system::Pallet::<T>::block_number() + T::SigningTimeout::get();
+			Expiries::<T, I>::mutate(expiry_block, |entries| {
+				entries.push((BroadcastStage::TransactionSigning, attempt_id))
+			});
+
+			// Emit the transaction signing request.
+			Self::deposit_event(Event::<T, I>::TransactionSigningRequest(
+				attempt_id,
+				nominated_signer,
+				unsigned_tx,
+			));
+		} else {
+			// In this case all validators are currently offline. We just do
+			// nothing in this case and wait until someone comes up again.
+			log::warn!("No online validators at the moment.");
+			let failed = FailedBroadcastAttempt::<T, I> {
 				broadcast_id,
 				attempt_count,
 				unsigned_tx: unsigned_tx.clone(),
-				nominee: nominated_signer.clone(),
-			},
-		);
-
-		// Schedule expiry.
-		let expiry_block = frame_system::Pallet::<T>::block_number() + T::SigningTimeout::get();
-		Expiries::<T, I>::mutate(expiry_block, |entries| {
-			entries.push((BroadcastStage::TransactionSigning, attempt_id))
-		});
-
-		// Emit the transaction signing request.
-		Self::deposit_event(Event::<T, I>::TransactionSigningRequest(
-			attempt_id,
-			nominated_signer,
-			unsigned_tx,
-		));
+			};
+			Self::schedule_retry(failed);
+		}
 	}
 
 	fn report_and_schedule_retry(signer: &T::ValidatorId, failed: FailedBroadcastAttempt<T, I>) {
```

### state-chain/pallets/cf-broadcast/src/mock.rs
```diff
@@ -73,8 +73,8 @@ pub const RANDOM_NOMINEE: u64 = 0xc001d00d as u64;
 impl SignerNomination for MockNominator {
 	type SignerId = u64;
 
-	fn nomination_with_seed(_seed: u64) -> Self::SignerId {
-		RANDOM_NOMINEE
+	fn nomination_with_seed(_seed: u64) -> Option<Self::SignerId> {
+		Some(RANDOM_NOMINEE)
 	}
 
 	fn threshold_nomination_with_seed(_seed: u64) -> Vec<Self::SignerId> {
```

### state-chain/pallets/cf-threshold-signature/src/mock.rs
```diff
@@ -94,7 +94,7 @@ impl MockNominator {
 impl cf_traits::SignerNomination for MockNominator {
 	type SignerId = u64;
 
-	fn nomination_with_seed(_seed: u64) -> Self::SignerId {
+	fn nomination_with_seed(_seed: u64) -> Option<Self::SignerId> {
 		unimplemented!("Single signer nomination not needed for these tests.")
 	}
 
```

### state-chain/runtime/src/chainflip.rs
```diff
@@ -240,15 +240,12 @@ pub struct BasicSignerNomination;
 impl cf_traits::SignerNomination for BasicSignerNomination {
 	type SignerId = AccountId;
 
-	fn nomination_with_seed(_seed: u64) -> Self::SignerId {
-		pallet_cf_validator::ValidatorLookup::<Runtime>::iter()
+	fn nomination_with_seed(_seed: u64) -> Option<Self::SignerId> {
+		let validators = pallet_cf_validator::ValidatorLookup::<Runtime>::iter()
 			.skip_while(|(id, _)| !<Online as cf_traits::IsOnline>::is_online(id))
 			.take(1)
-			.collect::<Vec<_>>()
-			.first()
-			.expect("Can only panic if all validators are offline.")
-			.0
-			.clone()
+			.collect::<Vec<_>>();
+		validators.first().map(|(id, _)| id.clone())
 	}
 
 	fn threshold_nomination_with_seed(_seed: u64) -> Vec<Self::SignerId> {
```

### state-chain/traits/src/lib.rs
```diff
@@ -457,7 +457,8 @@ pub trait SignerNomination {
 	type SignerId;
 
 	/// Returns a random live signer. The seed value is used as a source of randomness.
-	fn nomination_with_seed(seed: u64) -> Self::SignerId;
+	/// Returns None if no signers are live.
+	fn nomination_with_seed(seed: u64) -> Option<Self::SignerId>;
 
 	/// Returns a list of live signers where the number of signers is sufficient to author a
 	/// threshold signature. The seed value is used as a source of randomness.
```

### state-chain/traits/src/mocks/signer_nomination.rs
```diff
@@ -16,11 +16,11 @@ macro_rules! impl_mock_signer_nomination {
 		impl cf_traits::SignerNomination for MockSignerNomination {
 			type SignerId = $account_id;
 
-			fn nomination_with_seed(seed: u64) -> Self::SignerId {
-				CANDIDATES.with(|cell| {
+			fn nomination_with_seed(seed: u64) -> Option<Self::SignerId> {
+				Some(CANDIDATES.with(|cell| {
 					let candidates = cell.borrow();
 					candidates[seed as usize % candidates.len()].clone()
-				})
+				}))
 			}
 
 			fn threshold_nomination_with_seed(seed: u64) -> Vec<Self::SignerId> {
```
