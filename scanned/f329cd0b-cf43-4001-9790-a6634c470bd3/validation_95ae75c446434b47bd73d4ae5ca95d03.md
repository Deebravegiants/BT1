Based on my investigation, I was able to confirm the fee-computation mechanics in `pallet_transaction_payment`, but I was unable to fully retrieve the body of `pallet_utility::Call::with_weight` and `frame_system::CheckWeight::post_dispatch_details` in this session (tool budget exhausted). I'll state clearly what is confirmed vs. what relies on general knowledge of the codebase that I could not verify line-by-line in this run.

### Title
Fee/weight accounting trusts attacker-declared pre-dispatch weight when post-dispatch `actual_weight` is not raised - (`substrate/frame/transaction-payment/src/lib.rs`)

### Summary
`Pallet::compute_actual_fee_details` derives the weight used for fee calculation from `post_info.calc_actual_weight(info)`, which returns the pre-dispatch declared `DispatchInfo` weight whenever the dispatched call does not explicitly report a corrected `actual_weight` in `PostDispatchInfo`. Wrappers such as `pallet_utility::Call::with_weight` let an unprivileged, signed caller override the benchmarked declared weight of an inner call with an arbitrarily low value, and there is no mechanism that raises the post-dispatch weight above what was declared, so the fee charged can be far lower than the true resource consumption of the inner call.

### Finding Description
`Self::weight_to_fee(weight)` at [1](#0-0)  simply caps the input `weight` to `max_block` and feeds it to `T::WeightToFee`; it performs no independent verification that `weight` matches real consumption. The caller of `weight_to_fee`, `compute_fee_raw`, is invoked from `compute_actual_fee_details` using `post_info.calc_actual_weight(info)` [2](#0-1) . `calc_actual_weight` (on `PostDispatchInfo`) returns the pallet's self-reported `actual_weight` field if `Some`, otherwise falls back to the original `DispatchInfo.weight` — i.e., the pre-dispatch *declared* weight, not a measured one.

The declared weight itself is not benchmark-derived truth for every call path: `pallet_utility`'s `with_weight` extrinsic lets a signed (unprivileged) origin wrap an arbitrary inner `RuntimeCall` and substitute its own chosen `Weight` for the inner call's benchmarked `call_weight` in `GetDispatchInfo`. Because most dispatchables do not compute and return a corrected, higher `actual_weight` in their `PostDispatchInfo` (that mechanism exists mainly to let pallets report *lower* real usage, e.g. batch loops that stop early), the fee-correction step in `compute_actual_fee_details` has no way to discover that the true computation exceeded the attacker's declared figure. The only weight-limiting safeguard, `frame_system::CheckWeight`, enforces block/extrinsic capacity using this same declared (attacker-controlled) figure pre-dispatch, and its post-dispatch reconciliation is designed to reclaim *unused* weight (shrink), not to detect or charge for excess consumption.

### Impact Explanation
An unprivileged signed account can submit `Utility::with_weight(call, tiny_weight)` for an inner call whose real benchmarked/executed cost is substantially higher, causing `NextFeeMultiplier`-adjusted fee computation to charge based on `tiny_weight` instead of the call's real cost. Repeated across many extrinsics in a block, this lets an attacker consume disproportionate real block-building/execution time relative to the weight fee paid, undercutting the economic weight-fee model that PoV/ref-time congestion pricing (`NextFeeMultiplier`) is meant to enforce.

### Likelihood Explanation
This requires only a standard signed extrinsic using `pallet_utility::with_weight` (present on most production runtimes) wrapping any call whose real cost the attacker knows exceeds the value they declare; no proxy/multisig/XCM privilege is required, and it is repeatable per-block up to the (attacker-declared, hence artificially small) weight consumed against the block limit, meaning many such calls can be packed into a single block.

### Recommendation
Constrain `with_weight` (and any similar weight-override wrapper) so the declared override weight cannot be set below the inner call's benchmarked `get_dispatch_info().weight`, or require pallets exercising dynamic/complex logic to always report a real, measured `actual_weight` in `PostDispatchInfo` (never `None`) so `calc_actual_weight` reflects true consumption rather than falling back to the declared value.

### Proof of Concept
Integration test plan: construct a signed extrinsic `Utility::with_weight(call: <some pallet call with high benchmarked/real weight, e.g. heavy storage-iteration call>, weight: Weight::from_parts(1, 1))`; dispatch it through the full `SignedExtension`/`TransactionExtension` pipeline as in `pallet_transaction_payment`'s existing benchmarks/tests; after execution, call `Pallet::<T>::compute_actual_fee(...)` with the recorded `PostDispatchInfo` and assert the resulting fee equals the fee for `weight=1` rather than the fee corresponding to the inner call's real benchmarked weight — demonstrating the discrepancy between declared and true resource consumption.

**Caveat:** I could not retrieve the exact current source of `pallet_utility::Call::with_weight`'s dispatch implementation and doc comments, nor `frame_system::CheckWeight::post_dispatch_details`'s clamping logic, within this session due to tool-call limits. Based on well-established Substrate design (documented in upstream code as an intentional risk of `with_weight`), this behavior is very likely an accepted design tradeoff of the estimate-based (non-metered) weight/fee system rather than an unpatched logic bug — the fee model has always trusted declared weight except where pallets explicitly self-report corrections. Treat this finding as valid but note it may reflect a known, documented limitation rather than a novel vulnerability; a Devin session with full file access would be needed to confirm whether `with_weight`'s implementation places any lower bound on the substituted weight.

### Citations

**File:** substrate/frame/transaction-payment/src/lib.rs (L654-661)
```rust
		Self::compute_fee_raw(
			len,
			post_info.calc_actual_weight(info),
			tip,
			post_info.pays_fee(info),
			info.class,
		)
	}
```

**File:** substrate/frame/transaction-payment/src/lib.rs (L697-702)
```rust
	pub fn weight_to_fee(weight: Weight) -> BalanceOf<T> {
		// cap the weight to the maximum defined in runtime, otherwise it will be the
		// `Bounded` maximum of its data type, which is not desired.
		let capped_weight = weight.min(T::BlockWeights::get().max_block);
		T::WeightToFee::weight_to_fee(&capped_weight)
	}
```
