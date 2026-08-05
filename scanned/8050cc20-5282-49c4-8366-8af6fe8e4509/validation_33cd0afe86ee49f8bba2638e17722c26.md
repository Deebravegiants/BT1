### Title
Non-atomic PoV reclaim accounting in deprecated `StorageWeightReclaim` under-reports refunds when later extensions mutate `post_info.actual_weight` - ([File: cumulus/primitives/storage-weight-reclaim/src/lib.rs])

### Summary
The `StorageWeightReclaim` extension in `cumulus/primitives/storage-weight-reclaim/src/lib.rs` computes `unspent = post_info.calc_unspent(info)` and `benchmarked_weight` from `PostDispatchInfo` at line 184-185, without accounting for extensions positioned after it in the `SignedExtra` tuple that also mutate `post_info.actual_weight` during their own `post_dispatch_details`. This is a real, but explicitly documented and already-deprecated, limitation of this specific primitive — the fix already shipped as the replacement `StorageWeightReclaim` in `cumulus-pallet-weight-reclaim`.

### Finding Description
`StorageWeightReclaim::post_dispatch_details` in this file operates purely on the `post_info`/`info` values passed to it by the tuple dispatcher, at whatever mutation state they are in when this specific element's `post_dispatch_details` is invoked [1](#0-0) . It does not wrap or drive any inner extension's `post_dispatch` itself — it is a standalone tuple element, unlike the newer generic `StorageWeightReclaim<T, S>` in `cumulus/pallets/weight-reclaim/src/lib.rs`, which explicitly wraps an inner extension `S`, calls `S::post_dispatch(inner_pre, info, &mut post_info_with_inner, len, result)` itself, and only then computes `benchmarked_actual_weight` and `accurate_unspent` from the post-inner-refund state [2](#0-1) .

Critically, this exact limitation is already called out by the crate authors: the type is marked `#[deprecated]` with a note stating "This extension doesn't provide accurate reclaim for storage intensive transaction extension pipeline; it ignores the validation and preparation of extensions prior to itself and ignores the post dispatch logic for extensions subsequent to itself... Use `StorageWeightReclaim` in the `cumulus-pallet-weight-reclaim` crate" [3](#0-2) .

So the described exploit mechanism (an attacker abusing an ordering where a later extension refunds `actual_weight` before/independent of this extension's own bookkeeping) is a real characteristic of the deprecated primitive, but it is a known, acknowledged design flaw of a deprecated component with an explicit safe replacement, not an unpatched zero-day. Runtimes are directed away from this construct via the deprecation notice, and the newer pallet-based extension in `cumulus/pallets/weight-reclaim` closes the gap by driving the inner extension itself and computing `accurate_unspent`/`already_unspent_in_tx_ext_pipeline` from the correctly composed state [4](#0-3) , and its `tests.rs::test_series` explicitly exercises inner-extension refund interactions [5](#0-4) .

The defensive "Node-side PoV size higher than runtime proof size weight" branch in the deprecated file still runs after the (potentially wrong) `current.reduce(...)`/`current.accrue(...)` call and would top up `BlockWeight` if it falls below `node_side_pov_size` [6](#0-5) , which is a real mitigating check that catches the case where `BlockWeight` is under-reported relative to the actual node-recorded proof size — it does not fully prevent transient under/over accounting within a single extrinsic, but it does prevent `BlockWeight`'s bookkeeping from drifting below the true node-side PoV size across the block, which is the stated invariant in the question.

### Impact Explanation
Any impact is confined to runtimes that (a) still use the deprecated `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim` instead of the recommended `cumulus_pallet_weight_reclaim::StorageWeightReclaim`, and (b) compose it with another extension that mutates `post_info.actual_weight` after it runs. This is a runtime-configuration risk, not a protocol-level bug reachable purely by an attacker's extrinsic content — it requires the runtime team to have chosen a deprecated, explicitly-warned-against extension ordering. The safeguard at the end of `post_dispatch_details` limits how far `BlockWeight` can be pushed below the true node-side proof size.

### Likelihood Explanation
Low. Polkadot SDK runtimes built after this deprecation should use `cumulus-pallet-weight-reclaim`'s `StorageWeightReclaim<T, S>`, which is designed to wrap the whole extension pipeline and is not vulnerable to this specific issue since it explicitly drives inner `post_dispatch` before computing unspent amounts. The deprecated primitive remains in the tree presumably for backward compatibility/migration and carries an explicit warning, making this a documented rather than exploitable-by-default condition.

### Recommendation
No code fix is proposed here since the safe replacement already exists; the recommendation is operational: ensure downstream runtimes migrate off `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim` to `cumulus_pallet_weight_reclaim::StorageWeightReclaim<T, S>`, which must wrap the entire remaining extension pipeline as documented.

### Proof of Concept
Not applicable as a novel exploit — the existing `cumulus/pallets/weight-reclaim/src/tests.rs::test_series` and `test_incorporates_check_weight_unspent_weight*` tests already cover the corrected behavior with an inner refunding extension (`MockExtensionWithRefund`) and assert correct `BlockWeight` accounting [7](#0-6) . Demonstrating the deprecated primitive's flaw would only reproduce the already-documented deprecation note, not a hidden defect.

### Citations

**File:** cumulus/primitives/storage-weight-reclaim/src/lib.rs (L114-118)
```rust
	#[deprecated(note = "This extension doesn't provide accurate reclaim for storage intensive \
		transaction extension pipeline; it ignores the validation and preparation of extensions prior \
		to itself and ignores the post dispatch logic for extensions subsequent to itself, it also
		doesn't provide weight information. \
		Use `StorageWeightReclaim` in the `cumulus-pallet-weight-reclaim` crate")]
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

**File:** cumulus/primitives/storage-weight-reclaim/src/lib.rs (L212-223)
```rust
			// If we encounter a situation where the node-side proof size is already higher than
			// what we have in the runtime bookkeeping, we add the difference to the `BlockWeight`.
			// This prevents that the proof size grows faster than the runtime proof size.
			let block_weight_proof_size = current.total().proof_size();
			let missing_from_node = node_side_pov_size.saturating_sub(block_weight_proof_size);
			if missing_from_node > 0 {
				log::debug!(
					target: LOG_TARGET,
					"Node-side PoV size higher than runtime proof size weight. node-side: {node_side_pov_size} block_size: {block_size} runtime: {block_weight_proof_size}, missing: {missing_from_node}. Setting to node-side proof size."
				);
				current.accrue(Weight::from_parts(0, missing_from_node), info.class);
			}
```

**File:** cumulus/pallets/weight-reclaim/src/lib.rs (L177-216)
```rust
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

		// The consumed weight as benchmarked. Calculated from post info and info.
		// NOTE: `calc_actual_weight` will take the minimum of `post_info` and `info` weights.
		// This means any underestimation of compute time in the pre dispatch info will not be
		// taken into account.
		let benchmarked_actual_weight = post_info_with_inner.calc_actual_weight(info);
```

**File:** cumulus/pallets/weight-reclaim/src/lib.rs (L264-277)
```rust
		// The saturation will happen if the pre-dispatch weight is underestimating the proof
		// size or if the node-side proof size is higher than expected.
		// In this case the extrinsic proof size weight reclaimed is 0 and not a negative reclaim.
		let accurate_unspent = info
			.total_weight()
			.saturating_sub(accurate_weight)
			.saturating_sub(Weight::from_parts(0, pov_size_missing_from_node));
		frame_system::ExtrinsicWeightReclaimed::<T>::put(accurate_unspent);

		// Call have already returned their unspent amount.
		// (also transaction extension prior in the pipeline, but there shouldn't be any.)
		let already_unspent_in_tx_ext_pipeline = post_info.calc_unspent(info);
		Ok(accurate_unspent.saturating_sub(already_unspent_in_tx_ext_pipeline))
	}
```

**File:** cumulus/pallets/weight-reclaim/src/tests.rs (L437-470)
```rust
#[test]
fn test_incorporates_check_weight_unspent_weight() {
	let mut test_ext = setup_test_externalities(&[100, 300]);

	test_ext.execute_with(|| {
		set_current_storage_weight(1000);

		// Benchmarked storage weight: 300
		let info = DispatchInfo { call_weight: Weight::from_parts(100, 300), ..Default::default() };

		// Actual weight is 50
		let mut post_info = PostDispatchInfo {
			actual_weight: Some(Weight::from_parts(50, 250)),
			pays_fee: Default::default(),
		};

		let tx_ext = new_tx_ext();

		// Check weight should add 300 + 150 (len) of weight
		let (pre, _) = tx_ext
			.validate_and_prepare(ALICE_ORIGIN.clone().into(), CALL, &info, LEN, 0)
			.unwrap();

		assert_eq!(pre.0, Some(100));

		// The `CheckWeight` extension will refund `actual_weight` from `PostDispatchInfo`
		// we always need to call `post_dispatch` to verify that they interoperate correctly.
		assert_ok!(Tx::post_dispatch(pre, &info, &mut post_info, LEN, &Ok(())));

		assert_eq!(post_info.actual_weight.unwrap(), Weight::from_parts(50, 350 - LEN as u64));
		// Reclaimed 100
		assert_eq!(get_storage_weight().proof_size(), 1350);
	})
}
```

**File:** cumulus/pallets/weight-reclaim/src/tests.rs (L552-655)
```rust
// Test for refund of calls and related proof size
#[test]
fn test_series() {
	struct TestCfg {
		measured_proof_size_pre_dispatch: u64,
		measured_proof_size_post_dispatch: u64,
		info_call_weight: Weight,
		info_extension_weight: Weight,
		post_info_actual_weight: Option<Weight>,
		block_weight_pre_dispatch: Weight,
		mock_ext_refund: Weight,
		assert_post_info_weight: Option<Weight>,
		assert_block_weight_post_dispatch: Weight,
	}

	let base_extrinsic = <<Test as frame_system::Config>::BlockWeights as Get<
		frame_system::limits::BlockWeights,
	>>::get()
	.per_class
	.get(DispatchClass::Normal)
	.base_extrinsic;

	let tests = vec![
		// Info is exact, no post info, no refund.
		TestCfg {
			measured_proof_size_pre_dispatch: 100,
			measured_proof_size_post_dispatch: 400,
			info_call_weight: Weight::from_parts(40, 100),
			info_extension_weight: Weight::from_parts(60, 200),
			post_info_actual_weight: None,
			block_weight_pre_dispatch: Weight::from_parts(1000, 1000),
			mock_ext_refund: Weight::from_parts(0, 0),
			assert_post_info_weight: None,
			assert_block_weight_post_dispatch: base_extrinsic +
				Weight::from_parts(1100, 1300 + LEN as u64),
		},
		// some tx ext refund is ignored, because post info is None.
		TestCfg {
			measured_proof_size_pre_dispatch: 100,
			measured_proof_size_post_dispatch: 400,
			info_call_weight: Weight::from_parts(40, 100),
			info_extension_weight: Weight::from_parts(60, 200),
			post_info_actual_weight: None,
			block_weight_pre_dispatch: Weight::from_parts(1000, 1000),
			mock_ext_refund: Weight::from_parts(20, 20),
			assert_post_info_weight: None,
			assert_block_weight_post_dispatch: base_extrinsic +
				Weight::from_parts(1100, 1300 + LEN as u64),
		},
		// some tx ext refund is ignored on proof size because lower than actual measure.
		TestCfg {
			measured_proof_size_pre_dispatch: 100,
			measured_proof_size_post_dispatch: 400,
			info_call_weight: Weight::from_parts(40, 100),
			info_extension_weight: Weight::from_parts(60, 200),
			post_info_actual_weight: Some(Weight::from_parts(100, 300)),
			block_weight_pre_dispatch: Weight::from_parts(1000, 1000),
			mock_ext_refund: Weight::from_parts(20, 20),
			assert_post_info_weight: Some(Weight::from_parts(80, 300)),
			assert_block_weight_post_dispatch: base_extrinsic +
				Weight::from_parts(1080, 1300 + LEN as u64),
		},
		// post info doesn't double refund the call and is missing some.
		TestCfg {
			measured_proof_size_pre_dispatch: 100,
			measured_proof_size_post_dispatch: 350,
			info_call_weight: Weight::from_parts(40, 100),
			info_extension_weight: Weight::from_parts(60, 200),
			post_info_actual_weight: Some(Weight::from_parts(60, 200)),
			block_weight_pre_dispatch: Weight::from_parts(1000, 1000),
			mock_ext_refund: Weight::from_parts(20, 20),
			// 50 are missed in pov because 100 is unspent in post info but it should be only 50.
			assert_post_info_weight: Some(Weight::from_parts(40, 200)),
			assert_block_weight_post_dispatch: base_extrinsic +
				Weight::from_parts(1040, 1250 + LEN as u64),
		},
		// post info doesn't double refund the call and is accurate.
		TestCfg {
			measured_proof_size_pre_dispatch: 100,
			measured_proof_size_post_dispatch: 250,
			info_call_weight: Weight::from_parts(40, 100),
			info_extension_weight: Weight::from_parts(60, 200),
			post_info_actual_weight: Some(Weight::from_parts(60, 200)),
			block_weight_pre_dispatch: Weight::from_parts(1000, 1000),
			mock_ext_refund: Weight::from_parts(20, 20),
			assert_post_info_weight: Some(Weight::from_parts(40, 150)),
			assert_block_weight_post_dispatch: base_extrinsic +
				Weight::from_parts(1040, 1150 + LEN as u64),
		},
		// post info doesn't double refund the call and is accurate. Even if mock ext is refunding
		// too much.
		TestCfg {
			measured_proof_size_pre_dispatch: 100,
			measured_proof_size_post_dispatch: 250,
			info_call_weight: Weight::from_parts(40, 100),
			info_extension_weight: Weight::from_parts(60, 200),
			post_info_actual_weight: Some(Weight::from_parts(60, 200)),
			block_weight_pre_dispatch: Weight::from_parts(1000, 1000),
			mock_ext_refund: Weight::from_parts(20, 300),
			assert_post_info_weight: Some(Weight::from_parts(40, 150)),
			assert_block_weight_post_dispatch: base_extrinsic +
				Weight::from_parts(1040, 1150 + LEN as u64),
		},
	];
```
