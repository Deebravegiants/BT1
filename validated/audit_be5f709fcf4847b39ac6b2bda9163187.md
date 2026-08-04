### Title
Cross-extrinsic, cross-class contamination of `BlockWeight` via `ExtrinsicWeightReclaimed` in `StorageWeightReclaim::post_dispatch_details` - (File: cumulus/pallets/weight-reclaim/src/lib.rs)

### Summary
`frame_system::ExtrinsicWeightReclaimed` is written at the end of every extrinsic's `post_dispatch_details` with that extrinsic's own leftover/unspent weight, and it is read back as `already_reclaimed` at the very start of the *next* extrinsic's `BlockWeight::mutate` closure, but it is applied using the *next* extrinsic's `info.class` rather than the class that actually produced the value. When two consecutive extrinsics in the same block belong to different `DispatchClass`es, the leftover weight from extrinsic N is incorrectly folded into extrinsic N+1's class bucket in `frame_system::BlockWeight`.

### Finding Description
At the end of `post_dispatch_details` [1](#0-0) , `accurate_unspent` — the residual/overestimated weight belonging to the *current* extrinsic's own `DispatchClass` — is stored unconditionally into the global `frame_system::ExtrinsicWeightReclaimed` value with no per-class tagging.

On the *next* extrinsic's `post_dispatch_details` call, this stale value is read back as `already_reclaimed` and immediately merged into `frame_system::BlockWeight` under the new extrinsic's own `info.class`: [2](#0-1) 

`frame_system::ExtrinsicWeightReclaimed` is a plain, class-agnostic `Weight` value — it carries no information about which `DispatchClass` produced it. `PerDispatchClass::accrue`/`reduce` operate strictly per-class [3](#0-2) , so `BlockWeight::mutate` here silently attributes a `DispatchClass::Normal` extrinsic's unspent weight to the `DispatchClass::Operational` bucket (or vice versa) whenever consecutive extrinsics differ in class. The same class-agnostic pattern exists in the canonical `frame_system::Pallet::reclaim_weight` used by `CheckWeight`/`WeightReclaim` [4](#0-3) , confirming this is a structural property of the shared `ExtrinsicWeightReclaimed` storage item rather than something specific to one call site.

No signature, nonce, origin, or weight-limit check in the transaction pipeline defends against this, because the contamination happens purely in `post_dispatch` bookkeeping after both extrinsics have already been accepted and dispatched — a normal signed user simply needs to submit two ordinary extrinsics of different `DispatchClass` back-to-back (e.g. a `Normal` extrinsic followed by an `Operational` one, both of which are reachable through ordinary signed/unsigned dispatch, not privileged calls).

### Impact Explanation
The bug degrades the accuracy of `frame_system::BlockWeight`'s per-class accounting: weight legitimately belonging to one `DispatchClass` bucket is moved into the other class's bucket for that block. This weakens (but does not fully defeat) the intended isolation between `Normal` and `Operational` weight budgets — e.g. an `Operational` extrinsic can end up being credited with headroom that should have stayed in the `Normal` class, or a `Normal` class's tracked consumption can be inflated by an unrelated `Operational` extrinsic's leftover. The magnitude is bounded by a single extrinsic's own overestimation (at most its `info.total_weight()`), so it is an accounting-correctness/limit-isolation issue rather than an unbounded weight-limit bypass, but it does violate the "per-class weight isolation" invariant the pallet is documented to maintain.

### Likelihood Explanation
This requires no special privilege: any account can submit two consecutive extrinsics of different `DispatchClass` within the same block (e.g. a `Normal`-class transfer followed by an `Operational`-class call, both dispatchable by ordinary signed origins where the runtime defines `Operational` calls reachable by users). The condition is triggered on essentially every block that mixes dispatch classes, making it highly reproducible rather than a rare edge case, though the magnitude of the resulting cross-class skew is limited to each individual extrinsic's own weight-estimation error.

### Recommendation
Tag `ExtrinsicWeightReclaimed` (or an equivalent mechanism) with the `DispatchClass` it was produced for, and only accrue the "already reclaimed" credit back into `BlockWeight` under that original class rather than the class of whichever extrinsic happens to run next; alternatively, apply/settle the leftover credit synchronously within the same extrinsic's `post_dispatch_details` instead of deferring it to be picked up by the following extrinsic.

### Proof of Concept
Rust integration test in `cumulus/pallets/weight-reclaim/src/tests.rs` style:
1. Set `BlockWeight` for `DispatchClass::Normal` and `DispatchClass::Operational` to known baseline values.
2. Run extrinsic A with `info.class = DispatchClass::Normal` and a `post_info.actual_weight` significantly less than `info.call_weight`, producing a large `accurate_unspent`/`ExtrinsicWeightReclaimed` value.
3. Run extrinsic B with `info.class = DispatchClass::Operational` immediately after (same block, no reset of `ExtrinsicWeightReclaimed` in between).
4. Assert that `frame_system::BlockWeight::<Test>::get().get(DispatchClass::Normal)` does **not** include B's true weight and equals the expected value based solely on A's own accounting, and that `frame_system::BlockWeight::<Test>::get().get(DispatchClass::Operational)` is inflated/deflated by A's leftover `accurate_unspent` amount rather than reflecting only B's true consumption — demonstrating the cross-class leak instead of the two buckets staying independently accurate.

### Citations

**File:** cumulus/pallets/weight-reclaim/src/lib.rs (L235-239)
```rust
		let pov_size_missing_from_node = frame_system::BlockWeight::<T>::mutate(|current_weight| {
			let already_reclaimed = frame_system::ExtrinsicWeightReclaimed::<T>::get();
			current_weight.accrue(already_reclaimed, info.class);
			current_weight.reduce(info.total_weight(), info.class);
			current_weight.accrue(accurate_weight, info.class);
```

**File:** cumulus/pallets/weight-reclaim/src/lib.rs (L264-271)
```rust
		// The saturation will happen if the pre-dispatch weight is underestimating the proof
		// size or if the node-side proof size is higher than expected.
		// In this case the extrinsic proof size weight reclaimed is 0 and not a negative reclaim.
		let accurate_unspent = info
			.total_weight()
			.saturating_sub(accurate_weight)
			.saturating_sub(Weight::from_parts(0, pov_size_missing_from_node));
		frame_system::ExtrinsicWeightReclaimed::<T>::put(accurate_unspent);
```

**File:** substrate/frame/support/src/dispatch.rs (L502-521)
```rust
	/// Add some weight to the given class. Saturates at the numeric bounds.
	pub fn add(mut self, weight: Weight, class: DispatchClass) -> Self {
		self.accrue(weight, class);
		self
	}

	/// Increase the weight of the given class. Saturates at the numeric bounds.
	pub fn accrue(&mut self, weight: Weight, class: DispatchClass) {
		self.get_mut(class).saturating_accrue(weight);
	}

	/// Try to increase the weight of the given class. Saturates at the numeric bounds.
	pub fn checked_accrue(&mut self, weight: Weight, class: DispatchClass) -> Result<(), ()> {
		self.get_mut(class).checked_accrue(weight).ok_or(())
	}

	/// Reduce the weight of the given class. Saturates at the numeric bounds.
	pub fn reduce(&mut self, weight: Weight, class: DispatchClass) {
		self.get_mut(class).saturating_reduce(weight);
	}
```

**File:** substrate/frame/system/src/lib.rs (L2467-2487)
```rust
	pub fn reclaim_weight(
		info: &DispatchInfoOf<T::RuntimeCall>,
		post_info: &PostDispatchInfoOf<T::RuntimeCall>,
	) -> Result<(), TransactionValidityError>
	where
		T::RuntimeCall: Dispatchable<Info = DispatchInfo, PostInfo = PostDispatchInfo>,
	{
		let already_reclaimed = crate::ExtrinsicWeightReclaimed::<T>::get();
		let unspent = post_info.calc_unspent(info);
		let accurate_reclaim = already_reclaimed.max(unspent);
		// Saturation never happens, we took the maximum above.
		let to_reclaim_more = accurate_reclaim.saturating_sub(already_reclaimed);
		if to_reclaim_more != Weight::zero() {
			crate::BlockWeight::<T>::mutate(|current_weight| {
				current_weight.reduce(to_reclaim_more, info.class);
			});
			crate::ExtrinsicWeightReclaimed::<T>::put(accurate_reclaim);
		}

		Ok(())
	}
```
