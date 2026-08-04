### Title
Cross-extrinsic leakage of `ExtrinsicWeightReclaimed` causes under-credited block-weight refunds for a victim's subsequent extrinsic - (File: substrate/frame/system/src/extensions/weight_reclaim.rs, substrate/frame/system/src/extensions/check_weight.rs, and `frame_system::Pallet::reclaim_weight` in substrate/frame/system/src/lib.rs)

### Summary
`frame_system::Pallet::reclaim_weight` computes `accurate_reclaim = already_reclaimed.max(unspent)` using the value stored in `ExtrinsicWeightReclaimed`, a mechanism intended to deduplicate refunds when *both* `CheckWeight` and `WeightReclaim` call `reclaim_weight` for the *same* extrinsic's post-dispatch step. Both extension implementations funnel into the same `crate::Pallet::<T>::reclaim_weight` call, and the unit tests confirm the storage item is deliberately pre-seeded and read across calls, but no reset of `ExtrinsicWeightReclaimed` to a per-extrinsic baseline (e.g., in `note_extrinsic`) was found in the reviewed code, meaning a value written by one extrinsic's post-dispatch can be read as the `already_reclaimed` baseline for a completely different, later extrinsic in the same block.

### Finding Description
`WeightReclaim::post_dispatch_details` [1](#0-0)  and `WeightReclaim::bare_post_dispatch` [2](#0-1)  both call `crate::Pallet::<T>::reclaim_weight(info, post_info)`. The same function is also invoked identically by `CheckWeight::post_dispatch_details` and `CheckWeight::bare_post_dispatch` [3](#0-2) .

The unit tests demonstrate the exact semantics of `reclaim_weight`'s use of `ExtrinsicWeightReclaimed`: a caller seeds `ExtrinsicWeightReclaimed::<Test>::put(accurate_refund)` before invoking `post_dispatch_details`, and the function then compares this stored "already reclaimed" value against the freshly computed `unspent` for the *current* `info`/`post_info` pair, taking the max, and re-persisting that max back into `ExtrinsicWeightReclaimed` [4](#0-3) . This pattern is designed for the case where two extensions in the *same* extrinsic's pipeline (e.g. a chain that legitimately includes both `CheckWeight` and `WeightReclaim`, or a pallet like `cumulus-pallet-weight-reclaim` doing an earlier partial reclaim) call `reclaim_weight` twice for the same `info`/`post_info`.

Nothing in the reviewed extension code resets `ExtrinsicWeightReclaimed` at the start of processing a *new* extrinsic. Since `BlockWeight` and other per-block system storage persist across all extrinsics in a block (only reverted per-extrinsic on dispatch failure via the runtime's own transactional wrapping, not proactively cleared between successful extrinsics), the last value written into `ExtrinsicWeightReclaimed` by extrinsic A's `reclaim_weight` call remains in storage when extrinsic B's own post-dispatch step calls `reclaim_weight`. B's call then reads A's stale `unspent_A` as its `already_reclaimed` baseline instead of a fresh, extrinsic-scoped value, and computes `max(unspent_A, unspent_B)` instead of `max(0, unspent_B)`.

### Impact Explanation
Because the applied `BlockWeight` reduction is derived from `accurate_reclaim.saturating_sub(already_reclaimed)`, a stale non-zero `already_reclaimed` baseline can only cause the *delta actually credited back to `BlockWeight`* to be less than or equal to B's true `unspent_B`. Concretely:
- If `unspent_A > unspent_B`, B receives *no* weight refund at all, even though it genuinely used less than its charged weight.
- If `unspent_A < unspent_B`, B is only refunded `unspent_B - unspent_A`, an under-refund.

The net effect is that `BlockWeight` overstates the true consumed weight for extrinsic B, i.e., the refund baseline "leaks" from one extrinsic into another and under-credits it, exactly matching the scoped impact of a block-weight accounting asymmetry. This does not enable fund theft or double-refunding beyond the true unspent weight (the `max()` operation can never push the credited delta above `unspent_B`), so the direction of the bug is conservative/anti-throughput rather than an over-crediting exploit: it wastes block weight headroom and can cause the block to appear more full than it actually is, potentially causing `CheckWeight`'s block-fullness checks to reject subsequent legitimate extrinsics that should otherwise fit.

### Likelihood Explanation
The precondition — that a normal user's extrinsic (or any extrinsic) with a large `unspent` weight lands earlier in the same block as another extrinsic that also goes through `reclaim_weight` — is trivially reachable by any unprivileged account: submitting two ordinary signed extrinsics that use a call with a large declared `call_weight` but small `actual_weight` (e.g., a call that returns `Some(small_weight)` in its `PostDispatchInfo`) is sufficient to populate a large stale value in `ExtrinsicWeightReclaimed`. No proxy/multisig/XCM path is required. Exact control over which specific extrinsic follows is limited by block-author-controlled extrinsic ordering, but an attacker can simply chain several of their own weight-heavy-but-cheap-to-execute extrinsics in sequence, guaranteeing the effect strikes at least their own later transactions, and probabilistically any co-located transactions from other users when included in the same block.

### Recommendation
Scope `ExtrinsicWeightReclaimed` strictly to the current extrinsic: reset/kill it to a default (zero) value at the start of each extrinsic's execution (e.g., in `frame_system::Pallet::note_extrinsic` or equivalent per-extrinsic initialization hook invoked by `frame_executive::Executive::apply_extrinsic` before validation/preparation), so that any later `reclaim_weight` call for that extrinsic starts from a fresh baseline of zero rather than inheriting a value written by a prior extrinsic.

### Proof of Concept
Rust integration test in the `frame_system` mock runtime:
1. Build extrinsic A whose `DispatchInfo.call_weight` is large and whose `PostDispatchInfo.actual_weight` is very small, so `unspent_A` is large; dispatch A through the full extension pipeline (`WeightReclaim` or `CheckWeight` as configured) and record `BlockWeight` after A.
2. Without manually resetting `ExtrinsicWeightReclaimed`, build extrinsic B with its own `DispatchInfo`/`PostDispatchInfo` where `unspent_B` is smaller than `unspent_A`, and dispatch B through the same pipeline in the same block.
3. Assert that `BlockWeight::<Test>::get()` after B equals `prior_weight_before_B + info_B.total_weight() - unspent_B` (i.e., B's own correct refund), and separately assert `crate::ExtrinsicWeightReclaimed::<Test>::get()` immediately before B's post-dispatch is non-zero and equal to `unspent_A` (proving contamination).
4. Expected (buggy) result: `BlockWeight` after B is higher than the correct value by `min(unspent_A, unspent_B)` (or the full `unspent_B` in the case `unspent_A >= unspent_B`), demonstrating B was under-refunded due to A's stale `ExtrinsicWeightReclaimed` value.

### Citations

**File:** substrate/frame/system/src/extensions/weight_reclaim.rs (L87-95)
```rust
	fn post_dispatch_details(
		_pre: Self::Pre,
		info: &DispatchInfoOf<T::RuntimeCall>,
		post_info: &PostDispatchInfoOf<T::RuntimeCall>,
		_len: usize,
		_result: &DispatchResult,
	) -> Result<Weight, TransactionValidityError> {
		crate::Pallet::<T>::reclaim_weight(info, post_info).map(|()| Weight::zero())
	}
```

**File:** substrate/frame/system/src/extensions/weight_reclaim.rs (L113-120)
```rust
	fn bare_post_dispatch(
		info: &DispatchInfoOf<T::RuntimeCall>,
		post_info: &mut PostDispatchInfoOf<T::RuntimeCall>,
		_len: usize,
		_result: &DispatchResult,
	) -> Result<(), TransactionValidityError> {
		crate::Pallet::<T>::reclaim_weight(info, post_info)
	}
```

**File:** substrate/frame/system/src/extensions/weight_reclaim.rs (L145-186)
```rust
	#[test]
	fn extrinsic_already_refunded_more_precisely() {
		new_test_ext().execute_with(|| {
			// This is half of the max block weight
			let info =
				DispatchInfo { call_weight: Weight::from_parts(512, 0), ..Default::default() };
			let post_info = PostDispatchInfo {
				actual_weight: Some(Weight::from_parts(128, 0)),
				pays_fee: Default::default(),
			};
			let prior_block_weight = Weight::from_parts(64, 0);
			let accurate_refund = Weight::from_parts(510, 0);
			let len = 0_usize;
			let base_extrinsic = block_weights().get(DispatchClass::Normal).base_extrinsic;

			// Set initial info
			BlockWeight::<Test>::mutate(|current_weight| {
				current_weight.set(prior_block_weight, DispatchClass::Normal);
				current_weight.accrue(
					base_extrinsic + info.total_weight() - accurate_refund,
					DispatchClass::Normal,
				);
			});
			crate::ExtrinsicWeightReclaimed::<Test>::put(accurate_refund);

			// Do the post dispatch
			assert_ok!(WeightReclaim::<Test>::post_dispatch_details(
				(),
				&info,
				&post_info,
				len,
				&Ok(())
			));

			// Ensure the accurate refund is used
			assert_eq!(crate::ExtrinsicWeightReclaimed::<Test>::get(), accurate_refund);
			assert_eq!(
				*BlockWeight::<Test>::get().get(DispatchClass::Normal),
				info.total_weight() - accurate_refund + prior_block_weight + base_extrinsic
			);
		})
	}
```

**File:** substrate/frame/system/src/extensions/check_weight.rs (L277-311)
```rust
	fn post_dispatch_details(
		_pre: Self::Pre,
		info: &DispatchInfoOf<T::RuntimeCall>,
		post_info: &PostDispatchInfoOf<T::RuntimeCall>,
		_len: usize,
		_result: &DispatchResult,
	) -> Result<Weight, TransactionValidityError> {
		crate::Pallet::<T>::reclaim_weight(info, post_info).map(|()| Weight::zero())
	}

	fn bare_validate(
		_call: &T::RuntimeCall,
		info: &DispatchInfoOf<T::RuntimeCall>,
		len: usize,
	) -> frame_support::pallet_prelude::TransactionValidity {
		Ok(Self::do_validate(info, len)?.0)
	}

	fn bare_validate_and_prepare(
		_call: &T::RuntimeCall,
		info: &DispatchInfoOf<T::RuntimeCall>,
		len: usize,
	) -> Result<(), TransactionValidityError> {
		let (_, next_len) = Self::do_validate(info, len)?;
		Self::do_prepare(info, len, next_len)
	}

	fn bare_post_dispatch(
		info: &DispatchInfoOf<T::RuntimeCall>,
		post_info: &mut PostDispatchInfoOf<T::RuntimeCall>,
		_len: usize,
		_result: &DispatchResult,
	) -> Result<(), TransactionValidityError> {
		crate::Pallet::<T>::reclaim_weight(info, post_info)
	}
```
