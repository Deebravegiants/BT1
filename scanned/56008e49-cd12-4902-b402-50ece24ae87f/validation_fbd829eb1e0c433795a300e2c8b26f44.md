### Title
`DynamicMaxBlockWeight` transaction-window state machine can be exhausted by crafted weight-refunding extrinsics, permanently denying full-core access for legitimate large extrinsics in the same block - ([File: cumulus/pallets/parachain-system/src/block_weight/transaction_extension.rs])

### Summary
`DynamicMaxBlockWeight::pre_validate_extrinsic`/`post_dispatch_extrinsic` implement a bounded "look-ahead window" (`MAX_TRANSACTION_TO_CONSIDER`, default 10) anchored at `first_transaction_index`, which is fixed the moment any transaction first triggers the over-`target_weight` check and never advances again while the block oscillates between `PotentialFullCore` and `FractionOfCore`. An unprivileged attacker can submit crafted transactions whose pre-dispatch declared weight exceeds `target_weight` (tripping `PotentialFullCore`) but whose post-dispatch actual weight (via legitimate `PostDispatchInfo::actual_weight` refund) stays under `target_weight`, forcing the mode back to `FractionOfCore` each time. Repeating this `MAX_TRANSACTION_TO_CONSIDER` times exhausts the window (based on raw extrinsic position, not on genuine full-core usage), so any legitimate large extrinsic submitted afterward in that block is rejected with `InvalidTransaction::ExhaustsResources`, even though the block never actually used full-core capacity.

### Finding Description
In `pre_validate_extrinsic` [1](#0-0) , when `info.total_weight().saturating_add(len).any_gt(target_weight)` is true, the code checks: [2](#0-1) 
`transaction_index - first_transaction_index < MAX_TRANSACTION_TO_CONSIDER` gates whether `PotentialFullCore` is entered or the extrinsic is rejected outright. Crucially, `first_transaction_index` is set once (via `.or(transaction_index)`) on the very first non-inherent extrinsic (whether it was a small one that just landed in `FractionOfCore` or a large one that triggered `PotentialFullCore`), and is never advanced again for the rest of the block [3](#0-2) [4](#0-3) .

In `post_dispatch_extrinsic`, when in `PotentialFullCore`, the decision to commit to `FullCore` versus reverting to `FractionOfCore` depends purely on whether the *actual* (post-refund) cumulative class weight exceeds `target_weight` [5](#0-4) . Because `DispatchInfo.total_weight()` used pre-dispatch is the caller's declared (worst-case) weight and `PostDispatchInfo::actual_weight` can legitimately refund it down to a much smaller value, an attacker fully controls whether the block "commits" to full core or bounces back to `FractionOfCore`. This exact bounce-back behavior is demonstrated by the existing unit test `tx_extension_large_tx_with_refund_goes_back_to_fractional` [6](#0-5) .

The existing test `tx_extension_large_tx_after_limit_is_rejected` [7](#0-6)  confirms that once the extrinsic index is `>= MAX_TRANSACTION_TO_CONSIDER` past `first_transaction_index`, a genuinely oversized extrinsic is rejected with `InvalidTransaction::ExhaustsResources` while the mode remains `FractionOfCore`, never having reached `FullCore`. Combining the two behaviors: an attacker submits `MAX_TRANSACTION_TO_CONSIDER` crafted "declared-heavy, refunded-light" transactions as the first extrinsics of the block. Each individually trips `PotentialFullCore` and then reverts to `FractionOfCore` in post-dispatch, consuming one "slot" of the position-based window without ever exhausting real block weight. By the time the legitimate large extrinsic (e.g., a runtime upgrade extrinsic) is processed, `transaction_index - first_transaction_index >= MAX_TRANSACTION_TO_CONSIDER`, so it falls into the `else` branch of the window check and is unconditionally rejected — regardless of dispatch class (`ALLOW_NORMAL` only affects `class_allowed`, not the window-exceeded branch) [8](#0-7) .

No existing check stops this: `class_allowed`, `is_first_block`, and the window check are all satisfied by the attacker's crafted transactions in the same way a legitimate one would be, and there is no mechanism that resets or advances `first_transaction_index` after an oscillation back to `FractionOfCore`, nor any accounting that distinguishes "attempted-but-refunded" heavy transactions from genuine light ones for purposes of the window.

### Impact Explanation
A block that never used full-core weight is left permanently unable to accept a legitimate oversized extrinsic (e.g., a runtime upgrade or any large operational call) submitted within that same first-block-of-core window, because the bounded attempt budget was consumed by cheap, weight-refunding transactions from an unprivileged attacker. This is a resource-accounting/state-convergence bug that causes denial-of-service against high-weight extrinsics for that block, matching the scoped impact.

### Likelihood Explanation
Preconditions are narrow but realistic: `DynamicMaxBlockWeight` with `ALLOW_NORMAL=true` (a documented default, `ALLOW_NORMAL: bool = true` [9](#0-8) ), and the target block being the first block of a core. The attacker needs only `MAX_TRANSACTION_TO_CONSIDER` (default 10) cheap transactions whose declared weight exceeds `target_weight` but which refund actual weight down (a normal SDK weight-refund pattern any pallet author or attacker-composed batch call can exploit) and must ensure these land before the legitimate extrinsic in the same block (achievable via tip/priority in an open, unprivileged mempool). This is fully repeatable every time such a block is produced.

### Recommendation
Anchor and advance the window based on actual attempted "over-target" transactions rather than a fixed `first_transaction_index` set once for the whole block, or track a counter of window attempts that only increments on transactions that actually enter the over-target branch and is reset/bounded independently of unrelated extrinsic positions. Additionally, consider only allowing the window mechanism to be consumed by transactions whose post-dispatch actual weight is close to their declared weight, or require that repeated bounce-backs (`PotentialFullCore` → `FractionOfCore`) do not silently consume the shared budget available to legitimate large extrinsics.

### Proof of Concept
Add to `cumulus/pallets/parachain-system/src/block_weight/tests.rs`:
1. Build test ext with `first_block_in_core(true)`, `number_of_cores(2)`.
2. Loop `i in 0..MAX_TRANSACTION_TO_CONSIDER` (10): set `System::set_extrinsic_index(i)`; construct `DispatchInfo` with `call_weight` = `target_weight + small_over_amount` (over target); call `TxExtension::validate_and_prepare(...)`; assert `Ok`, and assert mode is `PotentialFullCore { first_transaction_index: Some(0), .. }` on first iteration, `Some(fixed_idx)` thereafter; then call `post_dispatch` with `PostDispatchInfo { actual_weight: Some(small_refunded_weight), .. }` and assert mode reverts to `FractionOfCore`.
3. Set `System::set_extrinsic_index(MAX_TRANSACTION_TO_CONSIDER)`; construct a "legit" `DispatchInfo` with a genuinely large `call_weight` (e.g. runtime-upgrade-sized) and call `validate_and_prepare`.
4. Assert the result is `Err(InvalidTransaction::ExhaustsResources.into())` and that `crate::BlockWeightMode::<Runtime>::get()` never became `FullCore` for the block, proving the legitimate large extrinsic is denied despite the block never having used full-core capacity.

### Citations

**File:** cumulus/pallets/parachain-system/src/block_weight/transaction_extension.rs (L93-99)
```rust
pub struct DynamicMaxBlockWeight<
	Config,
	Inner,
	TargetBlockRate,
	const MAX_TRANSACTION_TO_CONSIDER: u32 = 10,
	const ALLOW_NORMAL: bool = true,
>(pub Inner, core::marker::PhantomData<(Config, TargetBlockRate)>);
```

**File:** cumulus/pallets/parachain-system/src/block_weight/transaction_extension.rs (L151-160)
```rust
				BlockWeightMode::<Config>::PotentialFullCore { first_transaction_index, .. } |
				BlockWeightMode::<Config>::FractionOfCore { first_transaction_index, .. } => {
					debug_assert!(
						!is_potential,
						"`PotentialFullCore` should resolve to `FullCore` or `FractionOfCore` after applying a transaction.",
					);

					let digest = frame_system::Pallet::<Config>::digest();
					let block_weight_over_limit = extrinsic_index == 0
						&& block_weight_over_target_block_weight::<Config, TargetBlockRate>();
```

**File:** cumulus/pallets/parachain-system/src/block_weight/transaction_extension.rs (L219-239)
```rust
						if transaction_index.unwrap_or_default().saturating_sub(first_transaction_index.unwrap_or_default()) < MAX_TRANSACTION_TO_CONSIDER
							&& is_first_block && class_allowed {
							log::trace!(
								target: LOG_TARGET,
								"Enabling `PotentialFullCore` mode for extrinsic",
							);

							*mode = Some(BlockWeightMode::<Config>::potential_full_core(
								// While applying inherents `extrinsic_index` and `first_transaction_index` will be `None`.
								// When the first transaction is applied, we want to store the index.
								first_transaction_index.or(transaction_index),
								target_weight,
							));
						} else {
							log::trace!(
								target: LOG_TARGET,
								"Transaction is over the block limit, but is either outside of the allowed window or the dispatch class is not allowed.",
							);

							return Err(InvalidTransaction::ExhaustsResources)
						}
```

**File:** cumulus/pallets/parachain-system/src/block_weight/transaction_extension.rs (L253-255)
```rust
						*mode =
							Some(BlockWeightMode::<Config>::fraction_of_core(first_transaction_index.or(transaction_index)));
					}
```

**File:** cumulus/pallets/parachain-system/src/block_weight/transaction_extension.rs (L321-355)
```rust
				BlockWeightMode::<Config>::PotentialFullCore {
					first_transaction_index,
					target_weight,
					..
				} => {
					let block_weight = frame_system::BlockWeight::<Config>::get();
					let extrinsic_class_weight = block_weight.get(info.class);

					// The transaction weight after execution is may not above the target weight,
					// but the full block weight is maybe now above the target weight.
					if extrinsic_class_weight.any_gt(*target_weight) ||
						block_weight_over_target_block_weight::<Config, TargetBlockRate>()
					{
						log::trace!(
							target: LOG_TARGET,
							"Extrinsic class weight {extrinsic_class_weight:?} above target weight {target_weight:?}, enabling `FullCore` mode."
						);

						*weight_mode = Some(BlockWeightMode::<Config>::full_core());

						// Inform the node that this block uses the full core.
						frame_system::Pallet::<Config>::deposit_log(
							CumulusDigestItem::UseFullCore.to_digest_item(),
						);
					} else {
						log::trace!(
							target: LOG_TARGET,
							"Extrinsic class weight {extrinsic_class_weight:?} not above target \
							weight {target_weight:?}, going back to `FractionOfCore` mode."
						);

						*weight_mode = Some(BlockWeightMode::<Config>::fraction_of_core(
							*first_transaction_index,
						));
					}
```

**File:** cumulus/pallets/parachain-system/src/block_weight/tests.rs (L365-415)
```rust
#[test]
fn tx_extension_large_tx_with_refund_goes_back_to_fractional() {
	TestExtBuilder::new()
		.number_of_cores(2)
		.first_block_in_core(true)
		.build()
		.execute_with(|| {
			initialize_block_finished();

			System::set_extrinsic_index(1);

			// Create a transaction larger than target weight
			let target_weight = MaximumBlockWeight::target_block_weight();
			let large_weight = target_weight
				.saturating_add(Weight::from_parts(WEIGHT_REF_TIME_PER_SECOND, 1024 * 1024));

			let info = DispatchInfo {
				call_weight: large_weight,
				class: DispatchClass::Normal,
				..Default::default()
			};

			assert_ok!(TxExtension::validate_and_prepare(
				TxExtension::new(Default::default()),
				SystemOrigin::Signed(0).into(),
				&CALL,
				&info,
				100,
				0,
			));

			assert_matches!(
				crate::BlockWeightMode::<Runtime>::get(),
				Some(BlockWeightMode::PotentialFullCore { first_transaction_index: Some(1), .. })
			);

			let mut post_info = PostDispatchInfo {
				actual_weight: Some(Weight::from_parts(5000, 5000)),
				pays_fee: Default::default(),
			};

			assert_ok!(TxExtension::post_dispatch((), &info, &mut post_info, 0, &Ok(())));

			assert_matches!(
				crate::BlockWeightMode::<Runtime>::get(),
				Some(BlockWeightMode::FractionOfCore { .. })
			);
			assert!(!has_use_full_core_digest());
			assert_eq!(MaximumBlockWeight::get(), target_weight);
		});
}
```

**File:** cumulus/pallets/parachain-system/src/block_weight/tests.rs (L509-547)
```rust
#[test]
fn tx_extension_large_tx_after_limit_is_rejected() {
	TestExtBuilder::new()
		.number_of_cores(2)
		.first_block_in_core(true)
		.build()
		.execute_with(|| {
			initialize_block_finished();

			// Set some index above the limit.
			System::set_extrinsic_index(20);

			// Create a transaction larger than target weight
			let target_weight = MaximumBlockWeight::target_block_weight();
			let large_weight = target_weight
				.saturating_add(Weight::from_parts(WEIGHT_REF_TIME_PER_SECOND, 1024 * 1024));

			let info = DispatchInfo { call_weight: large_weight, ..Default::default() };

			assert_eq!(
				TxExtension::validate_and_prepare(
					TxExtension::new(Default::default()),
					SystemOrigin::Signed(0).into(),
					&CALL,
					&info,
					100,
					0,
				)
				.unwrap_err(),
				InvalidTransaction::ExhaustsResources.into()
			);

			assert_eq!(
				crate::BlockWeightMode::<Runtime>::get(),
				Some(BlockWeightMode::fraction_of_core(None))
			);
			assert!(!has_use_full_core_digest());
		});
}
```
