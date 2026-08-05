This confirms a concrete, still-existing instance in the repository.

### Title
Legacy `cumulus-primitives-storage-weight-reclaim::StorageWeightReclaim` placed non-wrapping in `contracts-rococo` under-accounts proof size, causing `BlockWeight` over-reclaim - (File: cumulus/primitives/storage-weight-reclaim/src/lib.rs)

### Summary
The deprecated `StorageWeightReclaim` transaction extension in `cumulus_primitives_storage_weight_reclaim` only measures proof-size consumed between its own `prepare` and `post_dispatch_details` calls, not the whole extension pipeline. The `contracts-rococo` runtime still configures it as the last item of `SignedExtra` rather than wrapping the whole pipeline via the newer `cumulus_pallet_weight_reclaim::StorageWeightReclaim`, so proof size consumed by `frame_system::CheckNonZeroSender`, `CheckSpecVersion`, `CheckTxVersion`, `CheckGenesis`, `CheckEra`, `CheckNonce`, `CheckWeight`, and `pallet_transaction_payment::ChargeTransactionPayment` during their own `validate`/`prepare` phases (which run before the legacy extension's `prepare` snapshot) is never captured, letting `consumed_weight` understate real usage and `BlockWeight::mutate(...).reduce(...)` over-reclaim.

### Finding Description
The legacy extension takes its proof-size baseline in `prepare` [1](#0-0)  and computes the diff in `post_dispatch_details` against `get_proof_size()` at that later point [2](#0-1) . Because `TransactionExtension` tuples execute `validate`/`prepare` for each element strictly in pipeline order [3](#0-2) , any proof-size consumed by extensions earlier in the tuple (during their own `validate`/`prepare` storage reads) happens *before* `StorageWeightReclaim::prepare` takes its snapshot and is therefore invisible to the later diff computation. This is exactly the historical defect Parity itself documented and fixed by introducing a new *wrapping* extension: "prior to transaction extension, `StorageWeightReclaim` also missed the some proof size used by other transaction extension prior to itself. This is also fixed by the wrapping `StorageWeightReclaim`." [4](#0-3) 

The `cumulus-pallets/weight-reclaim` crate fixes this by having `StorageWeightReclaim<T, S>` itself be a wrapper generic over the whole inner extension tuple `S`, taking the proof-size snapshot in its own outer `validate`/`prepare` before any inner extension runs, and computing the diff in its own outer `post_dispatch_details` after all inner extensions' `post_dispatch` has run [5](#0-4) .

`contracts-rococo`'s runtime still uses the deprecated, non-wrapping form as the *last* element of a flat `SignedExtra` tuple, rather than the new wrapping `cumulus_pallet_weight_reclaim::StorageWeightReclaim<Runtime, (...)>` pattern used by asset-hub-rococo, bridge-hub-westend, coretime-westend, and the parachain template: [6](#0-5)  versus e.g. [7](#0-6) . In `contracts-rococo`'s configuration `CheckNonZeroSender`, `CheckSpecVersion`, `CheckTxVersion`, `CheckGenesis`, `CheckEra`, `CheckNonce`, `CheckWeight`, and `ChargeTransactionPayment` all run their `validate`/`prepare` before `StorageWeightReclaim::prepare` snapshots the proof size, so any storage reads these extensions perform (e.g. `ChargeTransactionPayment` reading balance/fee-related storage, `CheckNonce` reading account nonce, `CheckWeight` reading `BlockWeight`) contribute to the node-side PoV but are excluded from `consumed_weight`. The result is `benchmarked_actual_proof_size (from info) >= measured_proof_size (understated)`, so the code takes the `reduce` branch rather than `accrue`, reclaiming proof-size weight that was, in reality, at least partially consumed by the untracked preceding extensions [8](#0-7) . No existing check in this path bounds the reclaim against the preceding extensions' actual consumption; only the node-side vs. runtime-side "missing" comparison partially compensates, but only for total end-of-extrinsic PoV, and it is bounded by comparison to `current.total()` after the (already too-large) reduce, so under-reclaim is not fully caught in the common case where node-side proof size is still lower than the reduced `BlockWeight`.

### Impact Explanation
This causes `frame_system::BlockWeight` to be reduced by more than the extrinsic actually spared, allowing the collator/runtime to under-account real PoV usage across the block. Repeated over many extrinsics, this lets the parachain pack more real proof-of-validity bytes per block than `BlockWeight`/PoV limits intend, risking oversized PoV blocks relative to the runtime's own accounting — a parachain block-validity/DoS-adjacent risk as scoped, reachable by any signed user submitting ordinary extrinsics (no privilege required) since the vulnerable extensions (`CheckNonce`, `ChargeTransactionPayment`, etc.) execute on every signed transaction.

### Likelihood Explanation
Preconditions are met concretely in-repo: `contracts-rococo` still configures the deprecated, non-wrapping `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim<Runtime>` as the last extension in `SignedExtra`, with seven other proof/storage-touching extensions preceding it [6](#0-5) . Any normal signed extrinsic on this chain triggers the flawed accounting deterministically and repeatably; no attacker privilege beyond submitting a normal signed transaction is needed.

### Recommendation
Migrate `contracts-rococo` (and any other runtime still referencing `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim`) to the wrapping `cumulus_pallet_weight_reclaim::StorageWeightReclaim<Runtime, (...)>` extension that encompasses the entire `SignedExtra`/`TxExtension` pipeline, as already done in asset-hub-rococo, bridge-hub-westend, coretime-westend, and the parachain template, and remove/deny use of the deprecated standalone extension in production runtime configs.

### Proof of Concept
Unit test plan (extending `cumulus/primitives/storage-weight-reclaim/src/tests.rs` patterns): construct a mock preceding extension `MockExtensionConsumingProof` whose `prepare`/`validate` triggers a storage read that advances the proof-size recorder by a known amount (e.g. 50 bytes) *before* `StorageWeightReclaim::prepare` is invoked, mirroring `setup_test_externalities` proof recorder stepping already used in these tests [9](#0-8) . Build a tuple `(MockExtensionConsumingProof, StorageWeightReclaim<Test>)`, run `validate_and_prepare` then dispatch then `post_dispatch_details`, and assert that `get_storage_weight().total().proof_size()` after reclaim reflects the true total consumption including the mock extension's 50 bytes (i.e., reclaimed amount must not exceed `benchmarked - (mock_extension_consumption + call_consumption)`). Under the current code, the test should show the mock extension's consumption is excluded from `consumed_weight`, causing an over-reclaim equal to the mock extension's PoV usage — demonstrating the invariant "reclaimed weight must never exceed truly unused weight for the whole pipeline" is violated.

### Citations

**File:** cumulus/primitives/storage-weight-reclaim/src/lib.rs (L152-161)
```rust
	fn prepare(
		self,
		_val: Self::Val,
		_origin: &T::RuntimeOrigin,
		_call: &T::RuntimeCall,
		_info: &DispatchInfoOf<T::RuntimeCall>,
		_len: usize,
	) -> Result<Self::Pre, TransactionValidityError> {
		Ok(get_proof_size())
	}
```

**File:** cumulus/primitives/storage-weight-reclaim/src/lib.rs (L163-188)
```rust
	fn post_dispatch_details(
		pre: Self::Pre,
		info: &DispatchInfoOf<T::RuntimeCall>,
		post_info: &PostDispatchInfoOf<T::RuntimeCall>,
		_len: usize,
		_result: &DispatchResult,
	) -> Result<Weight, TransactionValidityError> {
		let Some(pre_dispatch_proof_size) = pre else {
			return Ok(Weight::zero());
		};

		let Some(post_dispatch_proof_size) = get_proof_size() else {
			log::debug!(
				target: LOG_TARGET,
				"Proof recording enabled during pre-dispatch, now disabled. This should not happen."
			);
			return Ok(Weight::zero());
		};
		// Unspent weight according to the `actual_weight` from `PostDispatchInfo`
		// This unspent weight will be refunded by the `CheckWeight` extension, so we need to
		// account for that.
		let unspent = post_info.calc_unspent(info).proof_size();
		let benchmarked_weight = info.total_weight().proof_size().saturating_sub(unspent);
		let consumed_weight = post_dispatch_proof_size.saturating_sub(pre_dispatch_proof_size);

		let storage_size_diff = benchmarked_weight.abs_diff(consumed_weight as u64);
```

**File:** cumulus/primitives/storage-weight-reclaim/src/lib.rs (L195-210)
```rust
		frame_system::BlockWeight::<T>::mutate(|current| {
			if consumed_weight > benchmarked_weight {
				log::error!(
					target: LOG_TARGET,
					"Benchmarked storage weight smaller than consumed storage weight. extrinsic: {} benchmarked: {benchmarked_weight} consumed: {consumed_weight} unspent: {unspent}",
					frame_system::Pallet::<T>::extrinsic_index().unwrap_or(0)
				);
				current.accrue(Weight::from_parts(0, storage_size_diff), info.class)
			} else {
				log::trace!(
					target: LOG_TARGET,
					"Reclaiming storage weight. extrinsic: {} benchmarked: {benchmarked_weight} consumed: {consumed_weight} unspent: {unspent}",
					frame_system::Pallet::<T>::extrinsic_index().unwrap_or(0)
				);
				current.reduce(Weight::from_parts(0, storage_size_diff), info.class)
			}
```

**File:** substrate/primitives/runtime/src/traits/transaction_extension/mod.rs (L601-612)
```rust
	fn prepare(
		self,
		val: Self::Val,
		origin: &<Call as Dispatchable>::RuntimeOrigin,
		call: &Call,
		info: &DispatchInfoOf<Call>,
		len: usize,
	) -> Result<Self::Pre, TransactionValidityError> {
		Ok(for_tuples!( ( #(
			Tuple::prepare(self.Tuple, val.Tuple, origin, call, info, len)?
		),* ) ))
	}
```

**File:** prdoc/stable2503/pr_6140.prdoc (L10-35)
```text
      For para chains `StorageWeightReclaim` in `cumulus-primitives-storage-weight-reclaim` is deprecated.
      A new transaction extension `StorageWeightReclaim` in `cumulus-pallet-weight-reclaim` is introduced.
      `StorageWeightReclaim` is meant to be used as a wrapping of the whole transaction extension pipeline, and will take into account all proof size accurately.

      The new wrapping transaction extension is used like this:
      ```rust
      /// The TransactionExtension to the basic transaction logic.
      pub type TxExtension = cumulus_pallet_weight_reclaim::StorageWeightReclaim<
             Runtime,
             (
                     frame_system::CheckNonZeroSender<Runtime>,
                     frame_system::CheckSpecVersion<Runtime>,
                     frame_system::CheckTxVersion<Runtime>,
                     frame_system::CheckGenesis<Runtime>,
                     frame_system::CheckEra<Runtime>,
                     frame_system::CheckNonce<Runtime>,
                     pallet_transaction_payment::ChargeTransactionPayment<Runtime>,
                     BridgeRejectObsoleteHeadersAndMessages,
                     (bridge_to_rococo_config::OnBridgeHubWestendRefundBridgeHubRococoMessages,),
                     frame_metadata_hash_extension::CheckMetadataHash<Runtime>,
                     frame_system::CheckWeight<Runtime>,
             ),
      >;
      ```

      NOTE: prior to transaction extension, `StorageWeightReclaim` also missed the some proof size used by other transaction extension prior to itself. This is also fixed by the wrapping `StorageWeightReclaim`.
```

**File:** cumulus/pallets/weight-reclaim/src/lib.rs (L148-210)
```rust
	fn validate(
		&self,
		origin: T::RuntimeOrigin,
		call: &T::RuntimeCall,
		info: &DispatchInfoOf<T::RuntimeCall>,
		len: usize,
		self_implicit: Self::Implicit,
		inherited_implication: &impl Implication,
		source: TransactionSource,
	) -> Result<(ValidTransaction, Self::Val, T::RuntimeOrigin), TransactionValidityError> {
		let proof_size = get_proof_size();

		self.0
			.validate(origin, call, info, len, self_implicit, inherited_implication, source)
			.map(|(validity, val, origin)| (validity, (proof_size, val), origin))
	}

	fn prepare(
		self,
		val: Self::Val,
		origin: &T::RuntimeOrigin,
		call: &T::RuntimeCall,
		info: &DispatchInfoOf<T::RuntimeCall>,
		len: usize,
	) -> Result<Self::Pre, TransactionValidityError> {
		let (proof_size, inner_val) = val;
		self.0.prepare(inner_val, origin, call, info, len).map(|pre| (proof_size, pre))
	}

	fn post_dispatch_details(
		pre: Self::Pre,
		info: &DispatchInfoOf<T::RuntimeCall>,
		post_info: &PostDispatchInfoOf<T::RuntimeCall>,
		len: usize,
		result: &DispatchResult,
	) -> Result<Weight, TransactionValidityError> {
		let (proof_size_before_dispatch, inner_pre) = pre;

		let mut post_info_with_inner = *post_info;
		S::post_dispatch(inner_pre, info, &mut post_info_with_inner, len, result)?;

		let inner_refund = if let (Some(before_weight), Some(after_weight)) =
			(post_info.actual_weight, post_info_with_inner.actual_weight)
		{
			before_weight.saturating_sub(after_weight)
		} else {
			Weight::zero()
		};

		let Some(proof_size_before_dispatch) = proof_size_before_dispatch else {
			// We have no proof size information, there is nothing we can do.
			return Ok(inner_refund);
		};

		let Some(proof_size_after_dispatch) = get_proof_size().defensive_proof(
			"Proof recording enabled during prepare, now disabled. This should not happen.",
		) else {
			return Ok(inner_refund);
		};

		// The consumed proof size as measured by the host.
		let measured_proof_size =
			proof_size_after_dispatch.saturating_sub(proof_size_before_dispatch);
```

**File:** cumulus/parachains/runtimes/contracts/contracts-rococo/src/lib.rs (L90-101)
```rust
/// The SignedExtension to the basic transaction logic.
pub type SignedExtra = (
	frame_system::CheckNonZeroSender<Runtime>,
	frame_system::CheckSpecVersion<Runtime>,
	frame_system::CheckTxVersion<Runtime>,
	frame_system::CheckGenesis<Runtime>,
	frame_system::CheckEra<Runtime>,
	frame_system::CheckNonce<Runtime>,
	frame_system::CheckWeight<Runtime>,
	pallet_transaction_payment::ChargeTransactionPayment<Runtime>,
	cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim<Runtime>,
);
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-rococo/src/lib.rs (L1157-1172)
```rust
/// The extension to the basic transaction logic.
pub type TxExtension = cumulus_pallet_weight_reclaim::StorageWeightReclaim<
	Runtime,
	(
		frame_system::AuthorizeCall<Runtime>,
		frame_system::CheckNonZeroSender<Runtime>,
		frame_system::CheckSpecVersion<Runtime>,
		frame_system::CheckTxVersion<Runtime>,
		frame_system::CheckGenesis<Runtime>,
		frame_system::CheckEra<Runtime>,
		frame_system::CheckNonce<Runtime>,
		frame_system::CheckWeight<Runtime>,
		pallet_asset_conversion_tx_payment::ChargeAssetTxPayment<Runtime>,
		frame_metadata_hash_extension::CheckMetadataHash<Runtime>,
	),
>;
```

**File:** cumulus/primitives/storage-weight-reclaim/src/tests.rs (L76-110)
```rust
#[test]
#[allow(deprecated)]
fn basic_refund() {
	// The real cost will be 100 bytes of storage size
	let mut test_ext = setup_test_externalities(&[0, 100]);

	test_ext.execute_with(|| {
		set_current_storage_weight(1000);

		// Benchmarked storage weight: 500
		let info = DispatchInfo { call_weight: Weight::from_parts(0, 500), ..Default::default() };
		let post_info = PostDispatchInfo::default();

		// Should add 500 + 150 (len) to weight.
		let (_, next_len) = CheckWeight::<Test>::do_validate(&info, LEN).unwrap();
		assert_ok!(CheckWeight::<Test>::do_prepare(&info, LEN, next_len));

		let (pre, _) = StorageWeightReclaim::<Test>(PhantomData)
			.validate_and_prepare(Some(ALICE.clone()).into(), CALL, &info, LEN, 0)
			.unwrap();
		assert_eq!(pre, Some(0));

		assert_ok!(CheckWeight::<Test>::post_dispatch_details((), &info, &post_info, 0, &Ok(()),));
		// We expect a refund of 400
		assert_ok!(StorageWeightReclaim::<Test>::post_dispatch_details(
			pre,
			&info,
			&post_info,
			LEN,
			&Ok(()),
		));

		assert_eq!(get_storage_weight().total().proof_size(), 1250);
	})
}
```
