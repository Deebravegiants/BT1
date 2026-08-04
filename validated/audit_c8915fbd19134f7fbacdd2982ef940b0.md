### Title
`WeightInfoExt::check_accuracy` never validates PoV (`proof_size`) accuracy of `enqueue_xcmp_messages`, only `ref_time` - ([File: cumulus/pallets/xcmp-queue/src/weights_ext.rs])

### Summary
The weight formula `WeightInfoExt::enqueue_xcmp_messages` is used to estimate the cost of `T::XcmpQueue::enqueue_messages` before `WeightMeter::can_consume` gates whether a batch of sibling-XCMP messages is processed. The only sanity check that this linear estimate tracks the real benchmarked cost, `check_accuracy`, exclusively compares `ref_time()` and completely ignores `proof_size()`, so an under-estimation of PoV cost for adversarial combinations of `first_page_pos`, `new_pages_count`, and message-size distribution would never be caught by this guard.

### Finding Description
`enqueue_xcmp_messages` builds an estimated `Weight` (both `ref_time` and `proof_size` components) by summing four independently-benchmarked overhead terms — `pages_overhead`, `messages_overhead`, `bytes_overhead`, and `pos_overhead` — each derived from single-parameter benchmarks (`enqueue_n_full_pages`, `enqueue_n_empty_xcmp_messages`, `enqueue_n_bytes_xcmp_message`, `enqueue_empty_xcmp_message_at`): [1](#0-0) 

The only automated check that this additive/linear approximation actually tracks the real cost measured by the composite benchmark `enqueue_1000_small_xcmp_messages` is `check_accuracy`: [2](#0-1) 

This check (a) only exercises a single fixed scenario — 1000 messages, 3000 bytes total, `new_pages_count: 0`, `first_page_pos` set to the *average* of `MaxMessageLen`, and `is_first_sender_batch = true` — and (b) the assertion (`approx::assert_relative_eq!`) compares only `estimated_weight.ref_time()` against `actual_weight.ref_time()`. `proof_size()` is never compared. Because the estimate is a sum of independently-benchmarked linear terms rather than a jointly-fit model, there is no guarantee that the composed `proof_size` estimate remains conservative (i.e., an upper bound) across combinations not covered by the single benchmarked scenario — e.g., worst-case `first_page_pos` near the end of a nearly-full page combined with a high `new_pages_count` and many small messages, which is exactly the batch shape controllable by a sibling chain's outbound HRMP/XCMP channel content (message count/size affect `get_batches_footprints`' `BatchFootprint`).

Since `check_accuracy` is the sole regression guard for this formula and it structurally cannot detect a `proof_size` mis-estimation, a future benchmark/weight change (or an existing untested corner case) that under-predicts `proof_size` for adversarial footprints would go undetected by CI/tests, while the formula's output still feeds `meter.can_consume` in the XCMP inbound processing path that gates real weight/PoV consumption of `handle_xcmp_messages` per the audit description.

### Impact Explanation
If the estimate under-predicts true PoV cost for a maliciously shaped batch (attacker crafts many small XCM messages via a sibling parachain's outbound channel, reachable by any user routing XCM cross-chain), `WeightMeter::can_consume` could accept a batch whose real `enqueue_messages` call consumes more proof size than budgeted. This can push actual proof-size consumption past the meter's permitted limit, which is an availability/accounting-integrity issue for the inbound XCMP message servicing path (`handle_xcmp_messages`), potentially causing that queue's PoV accounting to become inconsistent with the true block PoV, or causing the channel to be under-serviced/stalled once a corrupted meter forces overly conservative or fewer messages to be processed per block. This does not directly permit asset theft/duplication but does threaten "queue must not be halted by valid input" and "weight/PoV accounting must not be bypassable."

### Likelihood Explanation
Requires (1) a currently-unknown or future adversarial footprint combination for which the linear-sum estimate genuinely under-predicts `proof_size` relative to the real `enqueue_messages` PoV cost, and (2) an attacker able to shape sibling-channel message batches to hit that combination (feasible since message count/size/page layout are attacker-influenced via ordinary XCM sends that get routed through XCMP). The concrete, provable part of this finding is the test/regression gap itself (`check_accuracy` not checking `proof_size`); whether a currently-under-predicting combination exists in the shipped benchmarked constants cannot be confirmed without running the fuzz/benchmark comparison, so likelihood of an already-existing exploitable gap is unconfirmed but plausible and currently unguarded.

### Recommendation
Extend `check_accuracy` to also assert `proof_size()` accuracy (`approx::assert_relative_eq!` on `estimated_weight.proof_size()` vs `actual_weight.proof_size()`), and broaden its input space beyond the single average-case scenario to include boundary values of `first_page_pos` (0 and `MaxMessageLen::get()`), high `new_pages_count`, and `is_first_sender_batch = false`, ideally via a fuzz/property test that compares the composed estimate against directly-measured PoV for many `BatchFootprint` combinations, failing if the estimate is ever lower than the measured cost (must be a conservative upper bound, not just "close on average").

### Proof of Concept
Add a property/fuzz test in `cumulus/pallets/xcmp-queue/src/tests.rs` (or a new `weights_ext` test) that:
1. Generates random `BatchFootprint { msgs_count, size_in_bytes, new_pages_count }` and `first_page_pos` values (including edge values: `first_page_pos` near `MaxMessageLen`, `new_pages_count` at max allowed pages, `msgs_count` at max batch size), plus `is_first_sender_batch` in `{true, false}`.
2. For each combination, benchmarks the real `T::XcmpQueue::enqueue_messages` PoV consumption for that exact input shape (using the pallet's benchmarking harness) as `actual`.
3. Computes `estimated = WeightInfoExt::enqueue_xcmp_messages(first_page_pos, &footprint, is_first_sender_batch)`.
4. Asserts `estimated.proof_size() >= actual.proof_size()` (i.e., the estimate must never under-predict), failing the test and printing the offending footprint/position if violated — demonstrating concretely whether `search_best_by`-selected batches can be crafted where `meter.can_consume` would wrongly accept an over-limit batch.

### Citations

**File:** cumulus/pallets/xcmp-queue/src/weights_ext.rs (L33-82)
```rust
	fn enqueue_xcmp_messages(
		first_page_pos: u32,
		batch_footprint: &BatchFootprint,
		is_first_sender_batch: bool,
	) -> Weight {
		let message_count = batch_footprint.msgs_count.saturated_into();
		let size_in_bytes = batch_footprint.size_in_bytes.saturated_into();

		// The cost of adding `n` empty pages on the message queue.
		let pages_overhead = {
			let full_message_overhead = Self::enqueue_n_full_pages(1)
				.saturating_sub(Self::enqueue_n_empty_xcmp_messages(1));
			let n_full_messages_overhead =
				full_message_overhead.saturating_mul(batch_footprint.new_pages_count as u64);

			Self::enqueue_n_full_pages(batch_footprint.new_pages_count)
				.saturating_sub(Self::enqueue_n_full_pages(0))
				.saturating_sub(n_full_messages_overhead)
		};

		// The overhead of enqueueing `n` empty messages on the message queue.
		let messages_overhead = {
			Self::enqueue_n_empty_xcmp_messages(message_count)
				.saturating_sub(Self::enqueue_n_empty_xcmp_messages(0))
		};

		// The overhead of enqueueing `n` bytes on the message queue.
		let bytes_overhead = {
			Self::enqueue_n_bytes_xcmp_message(size_in_bytes)
				.saturating_sub(Self::enqueue_n_bytes_xcmp_message(0))
		};

		// If the messages are not added to the beginning of the first page, the page will be
		// decoded and re-encoded once. Let's account for this.
		let pos_overhead = {
			let mut pos_overhead = Self::enqueue_empty_xcmp_message_at(first_page_pos)
				.saturating_sub(Self::enqueue_empty_xcmp_message_at(0));
			// We need to account for the PoV size of the first page in the message queue only the
			// first time when we access it.
			if !is_first_sender_batch {
				pos_overhead = pos_overhead.set_proof_size(0);
			}
			pos_overhead
		};

		pages_overhead
			.saturating_add(messages_overhead)
			.saturating_add(bytes_overhead)
			.saturating_add(pos_overhead)
	}
```

**File:** cumulus/pallets/xcmp-queue/src/weights_ext.rs (L84-101)
```rust
	fn check_accuracy<MaxMessageLen: bounded_collections::Get<u32>>(err_margin: f64) {
		assert!(err_margin < 1f64);

		let estimated_weight =
			Self::uncached_enqueue_xcmp_messages().saturating_add(Self::enqueue_xcmp_messages(
				get_average_page_pos(MaxMessageLen::get()),
				&BatchFootprint { msgs_count: 1000, size_in_bytes: 3000, new_pages_count: 0 },
				true,
			));
		let actual_weight = Self::enqueue_1000_small_xcmp_messages();

		// Check that the ref_time diff is less than err_margin
		approx::assert_relative_eq!(
			estimated_weight.ref_time() as f64,
			actual_weight.ref_time() as f64,
			max_relative = err_margin
		);
	}
```
