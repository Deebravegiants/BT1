### Title
Deprecated `StorageWeightReclaim::post_dispatch_details` under-accounts `frame_system::BlockWeight` when placed mid-pipeline, over-reclaiming proof-size weight - (File: cumulus/primitives/storage-weight-reclaim/src/lib.rs)

### Summary
The deprecated `StorageWeightReclaim::post_dispatch_details` measures `consumed_weight` only over the window between its own `prepare()` and `post_dispatch_details()` calls, not the full extrinsic. When any transaction extension placed *before* it in the pipeline (e.g. `CheckNonce`, `ChargeTransactionPayment`) reads/writes trie nodes, that proof-size consumption is invisible to the reclaimer, causing it to compare a full-extrinsic `benchmarked_weight` against an artificially small `consumed_weight`, which inflates `storage_size_diff` and over-reduces `frame_system::BlockWeight`.

### Finding Description
`StorageWeightReclaim::prepare` captures `pre_dispatch_proof_size = get_proof_size()` at its own position in the extension pipeline [1](#0-0) . Any earlier extension's `validate`/`prepare` proof-size consumption has already happened and is baked into the node-side proof recorder before this snapshot is taken, so it is permanently excluded from the later `consumed_weight` computation.

In `post_dispatch_details`, `consumed_weight = post_dispatch_proof_size.saturating_sub(pre_dispatch_proof_size)` only reflects proof growth from this extension's own `prepare()` to its own `post_dispatch_details()` [2](#0-1) , while `benchmarked_weight = info.total_weight().proof_size().saturating_sub(unspent)` is derived from the full `DispatchInfo` for the whole extrinsic [3](#0-2) . These two quantities are computed over mismatched windows: `benchmarked_weight` is total-extrinsic scope, `consumed_weight` is intra-pipeline-position scope.

When `consumed_weight <= benchmarked_weight` (the common case, now made more likely because `consumed_weight` is artificially low), the code takes the `else` branch and calls `current.reduce(Weight::from_parts(0, storage_size_diff), info.class)` on `frame_system::BlockWeight` [4](#0-3) . Because `storage_size_diff` is inflated by the unmeasured proof-size actually consumed by prior extensions, this reduces `BlockWeight` by more than was truly freed — i.e., the block's recorded proof-size weight is understated relative to the true node-side proof size that will be included in the PoV.

This is precisely the limitation stated in the deprecation note attached to the type: "it ignores the validation and preparation of extensions prior to itself and ignores the post dispatch logic for extensions subsequent to itself" [5](#0-4) . No check in the extension itself enforces or verifies that it must be the very first extension in the pipeline; placement is entirely a runtime-configuration choice, and `TransactionExtension` tuples do not statically prevent an earlier proof-size-consuming extension.

### Impact Explanation
Because `frame_system::BlockWeight` is used by `frame_system::CheckWeight`/block-fullness enforcement to decide whether further extrinsics fit and to bound the proof size the collator will include in the parachain block, systematically over-reducing it lets more extrinsics be packed into a block than the true accumulated storage proof actually supports. The result is under-accounted PoV weight in `BlockWeight`, which can allow the node-side proof size to grow beyond what runtime bookkeeping reflects, up to (and mitigated only partially by) the "missing_from_node" correction logic further down in the same function [6](#0-5)  — but that correction only fires when the *cumulative* node-side proof (including block_size) already exceeds bookkeeping; it does not fix per-extrinsic mis-measurement and can lag by whole extrinsics, allowing transient overpacking before the correction is applied.

### Likelihood Explanation
This requires only a legitimate-but-suboptimal runtime configuration: any parachain still using the deprecated `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim` (rather than the wrapping replacement in `cumulus-pallet-weight-reclaim`) with it placed anywhere other than the very first slot in the `SignedExtra`/`TxExtension` tuple. Given this configuration, every ordinary signed extrinsic that exercises proof-size-consuming extensions ahead of `StorageWeightReclaim` (e.g. `CheckNonce` reading the account's nonce trie node, `ChargeTransactionPayment` reading balance/fee-related storage) triggers the mis-measurement deterministically and repeatably — no special crafting beyond normal extrinsic submission is needed.

### Recommendation
Migrate off the deprecated `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim` to the wrapping `StorageWeightReclaim` from `cumulus-pallet-weight-reclaim`, which is designed to enclose the whole extension pipeline and avoid window mismatches. If the deprecated extension must remain supported, enforce (e.g. via a `construct_runtime`/tuple-position static assertion or a runtime metadata check at genesis) that it is always the first element of the transaction extension pipeline, and reject any pipeline configuration that fails this constraint.

### Proof of Concept
Rust unit/integration test plan (in `cumulus/primitives/storage-weight-reclaim/src/tests.rs` or a new integration test crate):
1. Build a mock `TxExtension` tuple: `(HeavyProofConsumingExtension, StorageWeightReclaim<T>)`, where `HeavyProofConsumingExtension::prepare` performs a storage read/write that measurably increases `storage_proof_size()` (simulate via the existing test host-function mock used in `tests.rs`).
2. Dispatch an extrinsic through this pipeline with a `DispatchInfo` weight approximating the *true* total proof consumption (heavy extension + call).
3. Record `frame_system::BlockWeight::<T>::get()` before and after dispatch, and independently record `storage_proof_size()` before the heavy extension's `prepare()` and after `StorageWeightReclaim::post_dispatch_details` runs (i.e., over the *entire* extrinsic).
4. Assert: `true_consumed = end_full_proof_size - start_full_proof_size` (measured across the whole extrinsic) is larger than `consumed_weight` as computed inside `post_dispatch_details` (which starts its window only at `StorageWeightReclaim::prepare`).
5. Assert the resulting reduction applied to `frame_system::BlockWeight` (`storage_size_diff` via the `reduce` branch) exceeds `benchmarked_weight - true_consumed`, demonstrating the over-reclaim/under-accounting relative to the correct full-extrinsic delta.

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

**File:** cumulus/primitives/storage-weight-reclaim/src/lib.rs (L203-210)
```rust
			} else {
				log::trace!(
					target: LOG_TARGET,
					"Reclaiming storage weight. extrinsic: {} benchmarked: {benchmarked_weight} consumed: {consumed_weight} unspent: {unspent}",
					frame_system::Pallet::<T>::extrinsic_index().unwrap_or(0)
				);
				current.reduce(Weight::from_parts(0, storage_size_diff), info.class)
			}
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
