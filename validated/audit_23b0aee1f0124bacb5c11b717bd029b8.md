### Title
DMQ/HRMP inbound message size accounting double-grants the same remaining-PoV headroom, allowing combined included message bytes to exceed the true remaining block PoV - (File: cumulus/pallets/parachain-system/src/lib.rs)

### Summary
`Pallet::messages_collection_size_limit()` computes a size cap as `min(max_block_pov / 6, remaining_block_weight().remaining().proof_size())` a single time in `do_create_inherent`, and that single value is reused verbatim for both the DMQ and HRMP abridging passes. When the true remaining PoV headroom (`remaining_proof_size`) is smaller than `max_block_pov / 6`, each queue is independently granted up to the *entire* remaining headroom, so the combined DMQ+HRMP bytes actually included can be up to 2x the real remaining PoV budget rather than being bounded by it once.

### Finding Description
`messages_collection_size_limit()` at [1](#0-0)  returns `(max_block_pov / 6).min(remaining_proof_size)`, where `remaining_proof_size` is the actual PoV headroom left in the block at the time of computation.

In `do_create_inherent`, this value is computed once into the local `messages_collection_size_limit` and then used to seed the DMQ abridging budget (`size_limit`), and — critically — is added *again, unmodified*, to whatever is left of `size_limit` after DMQ abridging, to form the HRMP budget: [2](#0-1) .

The design comment states the intent is that "each message passing mechanism can use 1/6 of the total block PoV ... in total 1/3 of the block PoV can be used for message passing" [3](#0-2) . That static 1/6-each split is fine when the block still has ≥1/3 of `max_block_pov` free. But the `.min(remaining_proof_size)` term is meant to additionally cap the budget by the block's *actual* remaining headroom in tighter conditions (e.g., after heavy `on_initialize` weight consumption by other pallets before the inherent is built). Because this same `remaining_proof_size`-derived cap is applied independently to DMQ and then again to HRMP (rather than being consumed/shared across both), whenever `remaining_proof_size < max_block_pov / 6`, each queue can still be abridged up to the full `remaining_proof_size`, so the sum of raw message bytes actually included in `set_validation_data` can reach ~`2 * remaining_proof_size`, exceeding the true remaining PoV that was measured only once.

`into_abridged` decides how many raw message bytes vs. hashed-only references are placed into the inherent Call, directly determining how many PoV bytes the resulting call/extrinsic will occupy on-chain [4](#0-3) . No later check re-validates that the *combined* DMQ+HRMP abridged size fits within the single `remaining_proof_size` measured at line ~1274; `enqueue_inbound_downward_messages` and its HRMP counterpart only validate MQC head correctness, not aggregate PoV budget [5](#0-4) .

### Impact Explanation
When both DMQ and HRMP are maximally utilized in the same relay-parent window (attacker-triggerable via a DMP-generating action, e.g. a reserve transfer, plus a sibling-chain HRMP send targeting the same para) and the parachain's remaining block PoV is already constrained below `max_block_pov / 6` at inherent-construction time, the collator can include up to roughly double the intended/available PoV headroom worth of raw inbound message bytes in `set_validation_data`. This causes PoV mis-accounting: the produced candidate block can end up with a PoV size larger than what was actually budgeted/available, risking rejection by relay-chain PoV-size validation (denial of block inclusion) or, if not otherwise caught, an understatement of true block size in on-chain accounting.

### Likelihood Explanation
This requires a specific precondition: the block's `remaining_block_weight().remaining().proof_size()` must already be below `max_block_pov / 6` at the moment `do_create_inherent` runs (i.e., non-inherent on_initialize weight already consumed most of the block's PoV budget), combined with both DMQ and HRMP being saturated near their respective abridging limits at the same relay block. This is a narrower precondition than a fully attacker-controlled scenario since the attacker does not directly control how much PoV prior on_initialize hooks consume; it depends on runtime/parachain configuration and block conditions. It is reproducible deterministically in a controlled test environment by priming `remaining_block_weight` to a small value and maximizing both queues.

### Recommendation
Compute `remaining_proof_size` once and decrement it as each queue consumes its share, e.g. track a single shared budget variable across both the DMQ and HRMP abridging calls (only cap each individually at `max_block_pov / 6`, and additionally cap the *sum* by the single `remaining_proof_size` value), instead of adding the same `messages_collection_size_limit` a second time at line 1301.

### Proof of Concept
Rust integration test in `cumulus/pallets/parachain-system` test module:
1. Configure `BlockWeights::max_block` proof_size to a known value `MAX`.
2. Force `frame_system::Pallet::<T>::remaining_block_weight()` to report a small remaining proof_size `R < MAX/6` (e.g. by registering extra weight via `register_extra_weight_unchecked` before calling `do_create_inherent`).
3. Construct `ParachainInherentData` with DMQ and HRMP message sets each individually exceeding `R` in raw byte size.
4. Call `Pallet::<T>::do_create_inherent(data)` and inspect the resulting `Call::set_validation_data { inbound_messages_data, .. }`.
5. Assert that `downward_messages.into_abridged` size + `horizontal_messages.into_abridged` size ≤ `R` (single computed `messages_collection_size_limit()`), and show the current implementation fails this assertion (combined size can approach `2*R`).

### Citations

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1264-1268)
```rust
	///
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

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1319-1367)
```rust
	fn enqueue_inbound_downward_messages(
		expected_dmq_mqc_head: relay_chain::Hash,
		downward_messages: AbridgedInboundDownwardMessages,
	) -> Weight {
		downward_messages.check_enough_messages_included_basic("DMQ");

		let mut dmq_head = <LastDmqMqcHead<T>>::get();

		let (messages, hashed_messages) = downward_messages.messages();
		let message_count = messages.len() as u32;
		let weight_used = T::WeightInfo::enqueue_inbound_downward_messages(message_count);
		if let Some(last_msg) = messages.last() {
			Self::deposit_event(Event::DownwardMessagesReceived { count: message_count });

			// Eagerly update the MQC head hash:
			for msg in messages {
				dmq_head.extend_downward(msg);
			}
			<LastDmqMqcHead<T>>::put(&dmq_head);
			Self::deposit_event(Event::DownwardMessagesProcessed {
				weight_used,
				dmq_head: dmq_head.head(),
			});

			let mut last_processed_msg =
				InboundMessageId { sent_at: last_msg.sent_at, reverse_idx: 0 };
			for msg in hashed_messages {
				dmq_head.extend_with_hashed_msg(msg);

				if msg.sent_at == last_processed_msg.sent_at {
					last_processed_msg.reverse_idx += 1;
				}
			}
			LastProcessedDownwardMessage::<T>::put(last_processed_msg);

			T::DmpQueue::handle_messages(downward_messages.bounded_msgs_iter());
		}

		// After hashing each message in the message queue chain submitted by the collator, we
		// should arrive to the MQC head provided by the relay chain.
		//
		// A mismatch means that at least some of the submitted messages were altered, omitted or
		// added improperly.
		assert_eq!(dmq_head.head(), expected_dmq_mqc_head, "DMQ head mismatch");

		ProcessedDownwardMessages::<T>::put(message_count);

		weight_used
	}
```
