Audit Report

## Title
DMQ/HRMP inbound message size accounting double-grants the same remaining-PoV headroom, allowing combined included message bytes to exceed the true remaining block PoV - (File: cumulus/pallets/parachain-system/src/lib.rs)

## Summary
`Pallet::messages_collection_size_limit()` computes `(max_block_pov / 6).min(remaining_proof_size)` once in `do_create_inherent`, and this same value is applied independently to both the DMQ and HRMP abridging passes rather than being shared/decremented across both, confirmed by reading the code directly. [1](#0-0)  As a result, when `remaining_proof_size` is less than `max_block_pov / 6`, DMQ and HRMP can each independently consume up to the full `remaining_proof_size` amount of raw message bytes, so the combined included bytes can approach `2 * remaining_proof_size`. [2](#0-1) 

## Finding Description
The code confirms the claim exactly: `messages_collection_size_limit` is computed once, used to seed `size_limit` for the DMQ `into_abridged` call, and then whatever remains of `size_limit` after DMQ processing has the *same* `messages_collection_size_limit` value added again for the HRMP `into_abridged` call. [3](#0-2)  The doc comment on `messages_collection_size_limit` explicitly documents this as intentional design: "each message passing mechanism can use 1/6 of the total block PoV ... in total 1/3 of the block PoV can be used for message passing." [4](#0-3)  This means DMQ and HRMP are treated as two *independent* 1/6-of-block-PoV budgets by design — not a single shared 1/3 budget — and the `.min(remaining_proof_size)` term is applied per-mechanism, consistent with that per-mechanism model, not as a single global cap meant to be consumed once across both queues.

The `into_abridged` mechanics were verified: it walks through messages, and stops including full messages once `size_limit` would be exceeded, hashing the remainder. [5](#0-4) 

Investigation into where `remaining_proof_size` actually comes from surfaced important context not covered by the claim: `remaining_block_weight()` is tied to Cumulus's newer dynamic block-weight/core-bundling mechanism (`block_weight/mod.rs`), which computes `MaxParachainBlockWeight` based on `FULL_CORE_WEIGHT`/`target_block_weight` per elastic-scaling core allocation, and toggles between "full core" and "fraction of core" weight budgets depending on block-bundle context. [6](#0-5)  This shows `remaining_block_weight()`/`BlockWeights::max_block` in modern Cumulus runtimes is a dynamically-adjusted, context-dependent value (not a static per-block constant), which complicates the claim's framing of "the true remaining block PoV" as a single fixed, precisely-known budget that is being violated by 2x.

I was unable to fully trace, within the available tool budget, whether `frame_system::Pallet::<T>::remaining_block_weight()` (defined in `substrate/frame/system/src/lib.rs`) is actually intended to be a strict, non-reusable, single-consumption PoV budget shared across all pallets in the same block, or whether each subsystem is expected to independently query and use fractions of it as a heuristic bound (as the "1/6 each, 1/3 total" doc comment suggests is the intended model here). Given the explicit doc comment describing the 1/6-per-mechanism/1/3-total design, the "double-grant" behavior appears to be the intended per-mechanism cap structure rather than an unintended bypass of a single global budget — the `.min(remaining_proof_size)` is a defensive additional clamp per mechanism, not evidence that the two mechanisms were meant to share one consumable pool.

## Impact Explanation
The report's core code-path description is accurate — `messages_collection_size_limit` is indeed added twice unmodified. However, whether this constitutes a real security vulnerability (as opposed to intended, если imprecise, design) is not established by the report. No code was found that treats `remaining_proof_size`-derived caps as a hard, aggregate accounting invariant meant to be consumed atomically across DMQ+HRMP; the surrounding doc explicitly describes independent 1/6 allocations. Additionally, actual PoV/candidate-size enforcement ultimately happens at relay-chain candidate validation (`max_pov_size`) and via the dynamic block-weight/core-bundling system, not solely via this heuristic — meaning an overrun here would likely surface as candidate PoV rejection at the relay chain layer (a normal, expected outcome of a collator submitting an oversized candidate) rather than an accounting/insolvency bug within the parachain-system pallet's own state.

## Likelihood Explanation
The precondition (remaining PoV already below `max_block_pov/6` at inherent-construction time, combined with both DMQ and HRMP saturated) is plausible but requires specific runtime conditions not directly controllable by an unprivileged attacker, and the report itself acknowledges this is not a fully attacker-controlled scenario.

## Recommendation
No specific code change is recommended without further confirmation of intended semantics; if a shared budget is intended, decrement a single tracked `remaining_proof_size` across both abridging passes instead of reusing `messages_collection_size_limit` twice.

## Proof of Concept
Not independently verified. The report's proposed integration test (priming `remaining_block_weight` to a small value via `register_extra_weight_unchecked`, then feeding oversized DMQ+HRMP message sets to `do_create_inherent` and asserting combined abridged size ≤ single `messages_collection_size_limit()`) is plausible as a demonstration of the described code behavior, but was not run or confirmed against this repository's test harness within this investigation.

### Citations

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1265-1268)
```rust
	/// The purpose of this limit is to make sure that the total size of the messages received by
	/// the parachain from the relay chain doesn't exceed the block size. Currently each message
	/// passing mechanism can use 1/6 of the total block PoV which means that in total 1/3
	/// of the block PoV can be used for message passing.
```

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1269-1277)
```rust
	fn messages_collection_size_limit() -> usize {
		let max_block_weight = <T as frame_system::Config>::BlockWeights::get().max_block;
		let max_block_pov = max_block_weight.proof_size();

		let remaining_proof_size =
			frame_system::Pallet::<T>::remaining_block_weight().remaining().proof_size();

		(max_block_pov / 6).min(remaining_proof_size).saturated_into()
	}
```

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1289-1302)
```rust
		let messages_collection_size_limit = Self::messages_collection_size_limit();
		// DMQ.
		let last_processed_msg = LastProcessedDownwardMessage::<T>::get()
			.unwrap_or(InboundMessageId { sent_at: last_relay_block_number, reverse_idx: 0 });
		downward_messages.drop_processed_messages(&last_processed_msg);
		let mut size_limit = messages_collection_size_limit;
		let downward_messages = downward_messages.into_abridged(&mut size_limit);

		// HRMP.
		let last_processed_msg = LastProcessedHrmpMessage::<T>::get()
			.unwrap_or(InboundMessageId { sent_at: last_relay_block_number, reverse_idx: 0 });
		horizontal_messages.drop_processed_messages(&last_processed_msg);
		size_limit = size_limit.saturating_add(messages_collection_size_limit);
		let horizontal_messages = horizontal_messages.into_abridged(&mut size_limit);
```

**File:** cumulus/pallets/parachain-system/src/block_weight/mod.rs (L187-292)
```rust
/// Calculates the maximum block weight for a parachain.
///
/// Based on the available cores and the number of desired blocks a block weight is calculated.
///
/// The max block weight is partly dynamic and controlled via the [`DynamicMaxBlockWeight`]
/// transaction extension. The transaction extension is communicating the desired max block weight
/// using the [`BlockWeightMode`].
pub struct MaxParachainBlockWeight<Config, TargetBlockRate>(PhantomData<(Config, TargetBlockRate)>);

impl<Config: crate::Config, TargetBlockRate: Get<u32>>
	MaxParachainBlockWeight<Config, TargetBlockRate>
{
	/// Returns the target block weight for one block.
	pub(crate) fn target_block_weight() -> Weight {
		let digest = frame_system::Pallet::<Config>::digest();
		Self::target_block_weight_with_digest(&digest)
	}

	/// Same as [`Self::target_block_weight`], but takes the `digests` directly.
	fn target_block_weight_with_digest(digest: &Digest) -> Weight {
		let number_of_cores = CumulusDigestItem::find_core_info(&digest).map_or_else(
			|| PreviousCoreCount::<Config>::get().map_or(1, |pc| pc.0),
			|ci| ci.number_of_cores.0,
		) as u64;

		let target_blocks = TargetBlockRate::get() as u64;

		// Ensure we have at least one core and valid target blocks
		if number_of_cores == 0 || target_blocks == 0 {
			return FULL_CORE_WEIGHT;
		}

		let blocks_per_core = target_blocks.div_ceil(number_of_cores);

		// At maximum we want to allow `6s` of ref time, because we don't want to overload nodes
		// that are running with standard hardware. These nodes need to be able to import all the
		// blocks in `6s`.
		let ref_time_per_block = core::cmp::min(
			MAX_REF_TIME_PER_CORE_NS / blocks_per_core, // Core allocation limit
			(6 * WEIGHT_REF_TIME_PER_SECOND) / target_blocks, // Full node import limit
		);

		// PoV size we can use as much as we can get from the cores, but at maximum it is one block
		// per core. Or in other words, one block can not span across multiple cores.
		let proof_size_per_block = MAX_POV_SIZE as u64 / blocks_per_core;

		Weight::from_parts(ref_time_per_block, proof_size_per_block)
	}
}

impl<Config: crate::Config, TargetBlockRate: Get<u32>> Get<Weight>
	for MaxParachainBlockWeight<Config, TargetBlockRate>
{
	fn get() -> Weight {
		let digest = frame_system::Pallet::<Config>::digest();
		let target_block_weight = Self::target_block_weight_with_digest(&digest);

		let maybe_full_core_weight = if is_first_block_in_core_with_digest(&digest).unwrap_or(false)
		{
			FULL_CORE_WEIGHT
		} else {
			target_block_weight
		};

		// Check if we are inside `pre_validate_extrinsic` of the transaction extension.
		//
		// When `pre_validate_extrinsic` calls this code, it is interested to know the
		// fractional `target_block_weight` which is then used to calculate the weight for each
		// dispatch class. Fractional weight is returned to detect transactions exceeding the
		// fractional target, enabling proper transition to `PotentialFullCore` mode.
		//
		// If `FullCore` mode is already enabled, the fractional target weight is not important
		// anymore.
		let in_pre_validate = inside_pre_validate::with(|v| *v).unwrap_or(false);

		match crate::BlockWeightMode::<Config>::get().filter(|m| !m.is_stale()) {
			// We allow the full core.
			Some(
				BlockWeightMode::<Config>::FullCore { .. } |
				BlockWeightMode::<Config>::PotentialFullCore { .. },
			) => FULL_CORE_WEIGHT,
			// We are in `pre_validate`.
			_ if in_pre_validate => target_block_weight,
			// Only use the fraction of a core.
			Some(BlockWeightMode::<Config>::FractionOfCore { first_transaction_index, .. }) => {
				let is_phase_finalization = frame_system::Pallet::<Config>::execution_phase()
					.map_or(false, |p| matches!(p, frame_system::Phase::Finalization));
				let inherents_applied = frame_system::Pallet::<Config>::inherents_applied();

				if first_transaction_index.is_none() && !is_phase_finalization && !inherents_applied
				{
					// We are running in the context of inherents, here we allow the
					// full core weight.
					maybe_full_core_weight
				} else {
					// If we are finalizing the block (e.g. `on_idle` is running and
					// `finalize_block`), running `on_poll` or nothing required more than the target
					// block weight, we only allow the target block weight.
					target_block_weight
				}
			},
			// We are in `on_initialize` or in an offchain context.
			None => maybe_full_core_weight,
		}
	}
}
```
