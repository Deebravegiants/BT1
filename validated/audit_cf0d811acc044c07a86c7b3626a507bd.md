### Title
Deprecated `StorageWeightReclaim` under-accounts preceding transaction-extension PoV cost, causing block-weight over-reclaim - (File: cumulus/primitives/storage-weight-reclaim/src/lib.rs)

### Summary
The deprecated `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim` extension records `pre_dispatch_proof_size` in its own `prepare` hook, which runs after any transaction extensions positioned earlier in the pipeline have already consumed proof size in their own `validate`/`prepare`. Because it only wraps extensions after it (or none), any storage-proof cost incurred by preceding extensions is invisible to its `consumed_weight` calculation, causing `frame_system::BlockWeight::<T>::mutate` to call `current.reduce(...)` with an inflated reclaim amount, under-counting real PoV usage in `BlockWeight`.

### Finding Description
`StorageWeightReclaim::prepare` (line 152-161) captures `get_proof_size()` as `pre_dispatch_proof_size` only at its own position in the extension pipeline: [1](#0-0) . Any proof-size-consuming work performed by a transaction extension placed *before* `StorageWeightReclaim` in the tuple (e.g. in `validate`/`prepare` of a preceding extension that reads chain storage) happens before this snapshot is taken, so that consumption is excluded from `consumed_weight` computed in `post_dispatch_details`: [2](#0-1) .

`benchmarked_weight` is derived from `info.total_weight()`, which does include the benchmarked/declared extension weight for the whole pipeline (per `DispatchInfo::total_weight()` semantics with `extension_weight`), while `consumed_weight` is only the proof-size delta measured from this extension's own late snapshot. This asymmetry means `benchmarked_weight` can appear larger than `consumed_weight` purely because the preceding extension's actual proof-size cost was never captured into the "consumed" side, even though it was properly counted on the "benchmarked" side. The `else` branch then calls `current.reduce(Weight::from_parts(0, storage_size_diff), info.class)` [3](#0-2) , reclaiming more block weight than was truly consumed by the whole extrinsic (call + all extensions), because part of the real PoV cost occurred before the measurement window started.

This exact gap is explicitly documented as fixed by the wrapping design in the newer extension: `prdoc/stable2503/pr_6140.prdoc` states "prior to transaction extension, `StorageWeightReclaim` also missed the some proof size used by other transaction extension prior to itself" [4](#0-3) , and the replacement `cumulus_pallet_weight_reclaim::StorageWeightReclaim<T, S>` is designed specifically to wrap the *entire* pipeline (`self.0.validate(...)` is called first, and `proof_size` is snapshotted before delegating to the inner extension `S`) so no preceding-extension cost is missed: [5](#0-4) .

Existing checks do not stop this: `frame_system::CheckWeight` only enforces the (already under-reported) `BlockWeight` figure, and there is no cross-check comparing node-side PoV to a fully-accurate proof-size budget for extensions preceding `StorageWeightReclaim` when it is used standalone (not as a full-pipeline wrapper). This is purely a runtime configuration exposure: it only manifests on chains whose `TxExtension` places one or more storage-touching extensions ahead of the deprecated `StorageWeightReclaim` in the tuple, rather than using it (or the new `cumulus_pallet_weight_reclaim::StorageWeightReclaim`) as the outermost wrapper as documented.

### Impact Explanation
On an affected chain, `BlockWeight`'s recorded proof-size can be reduced below the true node-side PoV consumption for extrinsics that combine a preceding storage-costly extension with the deprecated `StorageWeightReclaim`. Repeated over-reclaim across many extrinsics in a block allows a signed attacker to pack more such extrinsics into a block than the true PoV budget supports, risking oversized/invalid PoV at the relay chain or resource exhaustion for collators re-executing the block (parachain-level block-production DoS risk), rather than direct asset loss.

### Likelihood Explanation
This requires: (1) the chain still uses the deprecated `cumulus_primitives_storage_weight_reclaim::StorageWeightReclaim` instead of the fixed `cumulus_pallet_weight_reclaim::StorageWeightReclaim` wrapper, and (2) at least one transaction extension positioned before it in the `TxExtension` tuple that reads/writes storage (consuming proof size) during `validate`/`prepare`. This is a real, well-known, already-acknowledged limitation (per the prdoc), not a novel exploit, and is fully within reach of an ordinary signed user submitting a normal signed extrinsic — no special privileges are needed, only the runtime's pipeline ordering determines exposure.

### Recommendation
Migrate to `cumulus_pallet_weight_reclaim::StorageWeightReclaim<Runtime, (...)>` as the outermost wrapper of the entire transaction extension pipeline, as already documented in `prdoc/stable2503/pr_6140.prdoc` and `docs/sdk/src/guides/enable_pov_reclaim.rs`, and remove any remaining usage of the deprecated extension, especially where other storage-costly extensions precede it in the pipeline.

### Proof of Concept
Extend `cumulus/primitives/storage-weight-reclaim/src/tests.rs::test_larger_pre_dispatch_proof_size` by inserting a mock transaction extension with nonzero proof-size cost in its `prepare`/`validate` (executed via `.validate_and_prepare` before `StorageWeightReclaim::prepare` snapshots `get_proof_size()`), then:
1. Simulate the preceding extension consuming N bytes of proof size before `StorageWeightReclaim::prepare` runs.
2. Run `StorageWeightReclaim::post_dispatch_details` and assert that `frame_system::BlockWeight::<Test>::get().total().proof_size()` reflects true total consumption (benchmarked_weight of whole pipeline minus true total consumed, including the N bytes from the preceding extension) rather than the currently computed value that ignores the preceding extension's N-byte cost — showing the reclaimed amount is too large by N bytes.

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

**File:** cumulus/primitives/storage-weight-reclaim/src/lib.rs (L184-188)
```rust
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

**File:** prdoc/stable2503/pr_6140.prdoc (L35-35)
```text
      NOTE: prior to transaction extension, `StorageWeightReclaim` also missed the some proof size used by other transaction extension prior to itself. This is also fixed by the wrapping `StorageWeightReclaim`.
```

**File:** cumulus/pallets/weight-reclaim/src/lib.rs (L148-163)
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
```
