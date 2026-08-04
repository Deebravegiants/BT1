This confirms the mechanics: `pallet_meta_tx::Pallet::dispatch` at [1](#0-0)  takes an unrestricted `_origin` (any signed account can call it as relayer) and dispatches the embedded meta-tx via its `TransactionExtension` pipeline, which includes `frame_system::CheckNonce` as part of `MetaTxExtension` [2](#0-1) . A `Stale` error is defined precisely for a nonce-too-low condition [3](#0-2) , and the existing test `meta_tx_extension_work` demonstrates that incrementing the signer's nonce before the meta-tx dispatches causes it to fail with `Error::<Runtime>::Stale` [4](#0-3) .

### Title
Meta-transactions can be front-run to force atomic relayer batches (`Utility::batch_all`) to revert - (File: `substrate/frame/meta-tx/src/lib.rs`, `substrate/frame/utility/src/lib.rs`)

### Summary
`pallet_meta_tx::dispatch` accepts any caller as relayer and executes the embedded, publicly-gossiped meta-transaction through a `TransactionExtension` pipeline that includes `CheckNonce`. Because meta-transactions are meant to be shared with any interested relayer before being submitted [5](#0-4) , an attacker can observe a broadcast meta-tx and submit it themselves ahead of the intended relayer. If the intended relayer had bundled that meta-tx together with other unrelated users' meta-transactions inside a `pallet_utility::batch_all` call (an all-or-nothing atomic batch [6](#0-5) ), the pre-consumption of the nonce causes the bundled `MetaTx::dispatch` to fail with `Error::Stale`, and `batch_all`'s atomicity (`result.map_err(...)?` inside the loop, propagating the error and rolling back the whole batch, see [7](#0-6) ) reverts every other user's meta-transaction bundled in the same call, even though those were fully valid.

### Finding Description
- `pallet_meta_tx::Pallet::dispatch` at [8](#0-7)  ignores `_origin` for authorization purposes and dispatches whatever `meta_tx` is passed, deriving the actual origin from the embedded signature via `extension.dispatch_transaction`.
- The extension stack configured in the kitchensink runtime is `(VerifySignature, MetaTxMarker, CheckNonZeroSender, CheckSpecVersion, CheckTxVersion, CheckGenesis, CheckEra, CheckNonce, CheckMetadataHash)` [2](#0-1) , meaning nonce validation (front-runnable) gates every meta-tx dispatch, exactly like `use_permit`'s nonce gates the Angstrom-style permit.
- `pallet_utility::batch_all` is explicitly documented and implemented to roll back the *entire* batch if any single call fails [6](#0-5) , confirmed by the `batch_all_revert` test [9](#0-8) .
- A relayer that batches several users' `MetaTx::dispatch` calls together via `batch_all` (to save on extrinsic overhead/fees) creates exactly the "bundle with an externally-consumable, signature-gated sub-call" pattern from the Angstrom report: anyone can front-run one meta-tx's nonce, forcing `Stale`, and that failure propagates up through `batch_all` to revert the whole bundle.

### Impact Explanation
Any account can grief a relayer's batched meta-transaction submission by extracting one of the publicly shared meta-transactions and resubmitting it directly (paying only the fee for that single meta-tx dispatch) before the relayer's batch lands. This forces the relayer's entire `batch_all` transaction to fail, wasting the relayer's transaction fee and weight, and delaying/failing delivery of all other unrelated, valid users' meta-transactions bundled in that call. This is a griefing/DoS on relayer economics and meta-tx delivery, directly analogous in mechanism and severity class to the original medium-risk finding.

### Likelihood Explanation
Likelihood depends entirely on relayer implementation choice: `pallet-meta-tx` itself does not use `batch_all` to bundle multiple users' meta-transactions — that would be an application/relayer-level design decision built on top of the pallet. Nothing in the reviewed in-scope FRAME code (`pallet-meta-tx`, `pallet-utility`) forces or even suggests this batching pattern; the pallet's own dispatch path handles one meta-tx per extrinsic and is not, by itself, vulnerable to this class of bundling-induced DoS. Consequently, exploitation requires a specific relayer implementation choice outside the pallets reviewed here.

### Recommendation
If a relayer (or any pallet built on top of `pallet-meta-tx`) intends to submit multiple independent meta-transactions atomically, it should use a non-atomic mechanism (e.g. `pallet_utility::batch` / `force_batch`, which continue past individual failures) rather than `batch_all`, or wrap each `MetaTx::dispatch` result so that one Stale/invalid meta-tx cannot cause unrelated ones to fail.

### Proof of Concept
1. Alice signs a meta-tx `M_A` (target call + `CheckNonce` extension at her current nonce `n`) and shares it publicly for relaying, per the pallet's documented flow [5](#0-4) .
2. A relayer bundles `M_A` with Bob's and Carol's valid meta-txs into one `RuntimeCall::Utility(batch_all { calls: [MetaTx::dispatch(M_A), MetaTx::dispatch(M_B), MetaTx::dispatch(M_C)] })` and submits it.
3. An attacker, having seen `M_A` on the gossip layer, submits `RuntimeCall::MetaTx::dispatch(M_A)` directly in an earlier block/position, consuming Alice's nonce `n`.
4. When the relayer's batch executes, `MetaTx::dispatch(M_A)` now fails with `Error::<Runtime>::Stale` (as directly demonstrated by the existing `meta_tx_extension_work` test which forces this exact error by pre-incrementing the nonce [4](#0-3) ), and because it's inside `batch_all`, the whole batch (including Bob's and Carol's calls) reverts [10](#0-9) .

**Caveat**: This finding requires a specific relayer/application design (atomic batching of multiple independent users' meta-transactions) that is not itself present or recommended anywhere in the in-scope `pallet-meta-tx` or `pallet-utility` code or docs I found. The core pallets, in isolation, are not vulnerable — `pallet-meta-tx::dispatch` handles one meta-tx per call, and its own tests confirm `Stale` failures are expected/handled behavior rather than an unexpected foot-gun. I flag it only as a plausible analog pattern per the requested methodology, not as a confirmed exploitable vulnerability in the reviewed pallets themselves.

### Citations

**File:** substrate/frame/meta-tx/src/lib.rs (L30-35)
```rust
//! The pallet provides a client-level API, typically not meant for direct use by end users.
//! A meta transaction, constructed with the help of a wallet, contains a target call, necessary
//! extensions, and the signer's signature. This transaction is then broadcast, and any interested
//! relayer can pick it up and execute it. The relayer submits a regular transaction via the
//! [`dispatch`](`Pallet::dispatch`) function, passing the meta transaction as an argument to
//! execute the target call on behalf of the signer while covering the fees.
```

**File:** substrate/frame/meta-tx/src/lib.rs (L141-157)
```rust
	#[pallet::error]
	pub enum Error<T> {
		/// Invalid proof (e.g. signature).
		BadProof,
		/// The meta transaction is not yet valid (e.g. nonce too high).
		Future,
		/// The meta transaction is outdated (e.g. nonce too low).
		Stale,
		/// The meta transactions's birth block is ancient.
		AncientBirthBlock,
		/// The transaction extension did not authorize any origin.
		UnknownOrigin,
		/// The meta transaction is invalid.
		Invalid,
		/// The meta transaction length is invalid.
		InvalidLength,
	}
```

**File:** substrate/frame/meta-tx/src/lib.rs (L191-215)
```rust
		pub fn dispatch(
			_origin: OriginFor<T>,
			meta_tx: Box<MetaTxFor<T>>,
			meta_tx_encoded_len: u32, // The size of the encoded meta transaction in bytes.
		) -> DispatchResultWithPostInfo {
			let origin = SystemOrigin::None;
			let meta_tx_size = meta_tx.encoded_size();
			ensure!(meta_tx_size <= meta_tx_encoded_len as usize, Error::<T>::InvalidLength);
			// `info` with worst-case call weight and extension weight.
			let info = {
				let mut info = meta_tx.call.get_dispatch_info();
				info.extension_weight = meta_tx.extension.weight(&meta_tx.call);
				info
			};
			// dispatch the meta transaction.
			let meta_dispatch_res = meta_tx
				.extension
				.dispatch_transaction(
					origin.into(),
					meta_tx.call,
					&info,
					meta_tx_size,
					meta_tx.extension_version,
				)
				.map_err(Error::<T>::from)?;
```

**File:** substrate/bin/node/runtime/src/lib.rs (L2664-2674)
```rust
pub type MetaTxExtension = (
	pallet_verify_signature::VerifySignature<Runtime>,
	pallet_meta_tx::MetaTxMarker<Runtime>,
	frame_system::CheckNonZeroSender<Runtime>,
	frame_system::CheckSpecVersion<Runtime>,
	frame_system::CheckTxVersion<Runtime>,
	frame_system::CheckGenesis<Runtime>,
	frame_system::CheckEra<Runtime>,
	frame_system::CheckNonce<Runtime>,
	frame_metadata_hash_extension::CheckMetadataHash<Runtime>,
);
```

**File:** substrate/frame/meta-tx/src/tests.rs (L304-312)
```rust
		// increment alice's nonce to invalidate the meta tx and verify that the
		// meta tx extension works.
		frame_system::Pallet::<Runtime>::inc_account_nonce(alice_account.clone());

		// Check Extrinsic validity and apply it.
		let result = apply_extrinsic(uxt);

		// Asserting the results.
		assert_eq!(result.unwrap_err().error, Error::<Runtime>::Stale.into());
```

**File:** substrate/frame/utility/src/lib.rs (L289-291)
```rust
		/// Send a batch of dispatch calls and atomically execute them.
		/// The whole transaction will rollback and fail if any of the calls failed.
		///
```

**File:** substrate/frame/utility/src/lib.rs (L323-347)
```rust
			for (index, call) in calls.into_iter().enumerate() {
				let info = call.get_dispatch_info();
				// If origin is root, bypass any dispatch filter; root can call anything.
				let result = if is_root {
					call.dispatch_bypass_filter(origin.clone())
				} else {
					let mut filtered_origin = origin.clone();
					// Don't allow users to nest `batch_all` calls.
					filtered_origin.add_filter(
						move |c: &<T as frame_system::Config>::RuntimeCall| {
							let c = <T as Config>::RuntimeCall::from_ref(c);
							!matches!(c.is_sub_type(), Some(Call::batch_all { .. }))
						},
					);
					call.dispatch(filtered_origin)
				};
				// Add the weight of this call.
				weight = weight.saturating_add(extract_actual_weight(&result, &info));
				result.map_err(|mut err| {
					// Take the weight of this function itself into account.
					let base_weight = T::WeightInfo::batch_all(index.saturating_add(1) as u32);
					// Return the actual used weight + base_weight of this call.
					err.post_info = Some(base_weight.saturating_add(weight)).into();
					err
				})?;
```

**File:** substrate/frame/utility/src/tests.rs (L591-617)
```rust
#[test]
fn batch_all_revert() {
	new_test_ext().execute_with(|| {
		let call = call_transfer(2, 5);
		let info = call.get_dispatch_info();

		assert_eq!(Balances::free_balance(1), 10);
		assert_eq!(Balances::free_balance(2), 10);
		let batch_all_calls = RuntimeCall::Utility(crate::Call::<Test>::batch_all {
			calls: vec![call_transfer(2, 5), call_transfer(2, 10), call_transfer(2, 5)],
		});
		assert_noop!(
			batch_all_calls.dispatch(RuntimeOrigin::signed(1)),
			DispatchErrorWithPostInfo {
				post_info: PostDispatchInfo {
					actual_weight: Some(
						<Test as Config>::WeightInfo::batch_all(2) + info.call_weight * 2
					),
					pays_fee: Pays::Yes
				},
				error: TokenError::FundsUnavailable.into(),
			}
		);
		assert_eq!(Balances::free_balance(1), 10);
		assert_eq!(Balances::free_balance(2), 10);
	});
}
```
