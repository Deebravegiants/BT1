This confirms the claim is accurate and current. `contracts-rococo` is the only remaining runtime in the repo still using the deprecated non-wrapping `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim<Runtime>` as the last extension in `SignedExtra`, alongside seven proof/storage-touching extensions that run before it and are excluded from the proof-size delta calculation.This confirms the deprecation note itself explicitly states the exact defect claimed: "it ignores the validation and preparation of extensions prior to itself and ignores the post dispatch logic for extensions subsequent to itself" [1](#0-0) . Combined with the confirmed `contracts-rococo` configuration still using this deprecated struct as the last element in `SignedExtra` behind seven storage/proof-touching extensions [2](#0-1) , the claim is substantiated by the code itself, not speculation.

Audit Report

## Title
Legacy `cumulus-primitives-storage-weight-reclaim::StorageWeightReclaim` placed non-wrapping in `contracts-rococo` under-accounts proof size, causing `BlockWeight` over-reclaim - (File: cumulus/primitives/storage-weight-reclaim/src/lib.rs)

## Summary
The deprecated `StorageWeightReclaim` transaction extension only measures proof-size consumed between its own `prepare` and `post_dispatch_details` calls, not the whole extension pipeline, as explicitly documented in its own deprecation note. `contracts-rococo` still configures this legacy extension as the last item of `SignedExtra` instead of migrating to the wrapping `cumulus_pallet_weight_reclaim::StorageWeightReclaim`, causing proof size consumed by the seven preceding extensions (`CheckNonZeroSender`, `CheckSpecVersion`, `CheckTxVersion`, `CheckGenesis`, `CheckEra`, `CheckNonce`, `CheckWeight`, `ChargeTransactionPayment`) during their `validate`/`prepare` phases to be excluded from the measured `consumed_weight`.

## Finding Description
`StorageWeightReclaim::prepare` snapshots proof size at that point in the pipeline [3](#0-2) , and `post_dispatch_details` computes the diff against a later snapshot [4](#0-3) . Since `TransactionExtension` tuples execute `validate`/`prepare` in strict order, any proof size consumed by earlier extensions in the tuple is invisible to this diff. This exact defect is acknowledged in the crate's own deprecation attribute: "it ignores the validation and preparation of extensions prior to itself" [1](#0-0) . `contracts-rococo` still places this deprecated extension as the last element of `SignedExtra`, after seven other proof/storage-touching extensions [2](#0-1) , whereas other runtimes have migrated to the wrapping `cumulus_pallet_weight_reclaim::StorageWeightReclaim<Runtime, (...)>` pattern that snapshots proof size before any inner extension runs.

## Impact Explanation
This causes `frame_system::BlockWeight` to be reduced (via the `reduce` branch in `post_dispatch_details`) by more than the extrinsic actually spared, since `consumed_weight` understates true proof-size usage. Repeated across ordinary signed extrinsics, this lets `contracts-rococo` under-account real PoV usage in `BlockWeight`, risking oversized PoV blocks relative to the runtime's own accounting.

## Likelihood Explanation
The precondition is met concretely and currently in the repository: `contracts-rococo`'s `SignedExtra` still references the deprecated non-wrapping extension as its last element. Any normal signed extrinsic on this chain deterministically triggers the flawed accounting; no special privilege is required beyond submitting an ordinary signed transaction.

## Recommendation
Migrate `contracts-rococo` to use `cumulus_pallet_weight_reclaim::StorageWeightReclaim<Runtime, (...)>` wrapping the entire `TxExtension`/`SignedExtra` pipeline, consistent with asset-hub-rococo, bridge-hub-westend, coretime-westend, and the parachain template, and remove reliance on the deprecated standalone extension in production runtime configs.

## Proof of Concept
Extend `cumulus/primitives/storage-weight-reclaim/src/tests.rs` with a mock preceding extension that advances the proof-size recorder by a known amount during its own `prepare`/`validate`, before `StorageWeightReclaim::prepare` snapshots proof size (mirroring the existing `setup_test_externalities` proof-recorder stepping pattern). Build a tuple `(MockExtensionConsumingProof, StorageWeightReclaim<Test>)`, run `validate_and_prepare` then dispatch then `post_dispatch_details`, and show that the mock extension's proof-size consumption is excluded from `consumed_weight`, causing `BlockWeight` to be reduced by more than the extrinsic truly spared.

### Citations

**File:** cumulus/primitives/storage-weight-reclaim/src/lib.rs (L114-118)
```rust
	#[deprecated(note = "This extension doesn't provide accurate reclaim for storage intensive \
		transaction extension pipeline; it ignores the validation and preparation of extensions prior \
		to itself and ignores the post dispatch logic for extensions subsequent to itself, it also
		doesn't provide weight information. \
		Use `StorageWeightReclaim` in the `cumulus-pallet-weight-reclaim` crate")]
```

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
