### Title
Malicious collator can permanently orphan (hash-skip) any suffix of the DMQ — including fee-bearing XCM messages — because DMP lacks the "advancement rule" check that HRMP enforces - ([File: cumulus/pallets/parachain-system/src/lib.rs])

### Summary
`enqueue_inbound_downward_messages` only calls `check_enough_messages_included_basic("DMQ")` on the collator-supplied `AbridgedInboundDownwardMessages`, unlike HRMP which additionally calls `check_enough_messages_included_advanced` (added specifically to close this gap, see `prdoc/stable2603/pr_9086.prdoc`). The basic check only requires "at least one full message" whenever any message is hashed; it never verifies that hashing was actually necessary given the real PoV budget. A collator can therefore hash (compress) a target message — and, by MQC-ordering necessity, every message after it in the queue — even though the message would have fit comfortably, causing the relay chain to permanently prune those messages once `ProcessedDownwardMessages` is reported, without them ever being dispatched to `T::DmpQueue`.

### Finding Description
`AbridgedInboundMessagesCollection::check_enough_messages_included_basic` (`cumulus/pallets/parachain-system/src/parachain_inherent.rs:173-184`) is the *only* rule applied to DMQ data in `enqueue_inbound_downward_messages` (`cumulus/pallets/parachain-system/src/lib.rs:1319-1367`, specifically line 1323). It merely asserts `full_messages.len() >= 1` whenever `hashed_messages` is non-empty — it does not check that the amount of "full" data included is as large as possible under `messages_collection_size_limit()`, the way `check_enough_messages_included_advanced` does for HRMP (`cumulus/pallets/parachain-system/src/lib.rs:1444-1455`, and `parachain_inherent.rs:192-218`).

Because `extend_downward` (applied to full messages) and `extend_with_hashed_msg` (applied to hashed/compressed messages) compute the identical hash contribution to the MQC head from `(sent_at, hash(data))`, the "full vs hashed" categorization has no effect on the resulting head — only the *order of application* matters. `enqueue_inbound_downward_messages` folds all `full_messages` first, then all `hashed_messages`. For the final head to equal `expected_dmq_mqc_head` (the relay-chain-verified head), the set of messages marked "full" must be exactly a prefix of the true DMQ order, and everything marked "hashed" must be the suffix.

This means: a malicious/censoring collator can freely choose the split point — including one that targets a specific fee-bearing XCM message (e.g. carrying `ReceiveTeleportedAsset`) — and place it (and everything after it) into the hashed suffix, regardless of whether it would have fit within `messages_collection_size_limit()`. `check_enough_messages_included_basic` is satisfied as long as one earlier dummy full message exists. The resulting call still passes `assert_eq!(dmq_head.head(), expected_dmq_mqc_head, "DMQ head mismatch")` at line 1362 because the hash chain is order-preserving and category-agnostic.

Once this block is included, `ProcessedDownwardMessages::<T>::put(message_count)` is submitted to the relay chain (via the candidate receipt), which prunes those messages from `DownwardMessageQueues`/`DownwardMessageQueueHeads` on the relay side (`polkadot/runtime/parachains/src/dmp.rs`). The hashed messages are never passed to `bounded_msgs_iter()`/`T::DmpQueue::handle_messages` (`lib.rs:1354`), so their XCM payload is never executed, and the relay-side data is gone forever — an irrecoverable loss, not merely a temporary delay.

### Impact Explanation
A collator (trusted only to relay/order data, not to control fund custody) can permanently prevent execution of any downward XCM message it targets, including asset-teleport/reserve-transfer messages, causing the sender-side funds to never be credited on the destination parachain while the relay chain considers the message "delivered/processed." This is a direct violation of "user-controlled assets must remain fully backed and cannot be ... permanently frozen" and "Critical queues and validation paths must not be permanently halted by valid user input," since the DMQ watermark and MQC head both advance normally, masking the loss. Note the collateral effect is that *all* subsequent DMQ messages are also stalled/orphaned (since the split must be a prefix/suffix), which is a stronger DoS than a surgical single-message skip, but still matches the scoped impact of "funds/XCM messages permanently stuck ... while state advances."

### Likelihood Explanation
Fully feasible with a single malicious or compromised collator turn, no special privileges beyond normal block authorship rights, and no chain-level detection mechanism (the only cross-check, the MQC head assertion, is satisfied by construction). It is repeatable every session such a collator is selected, and does not require the DMQ to actually exceed `messages_collection_size_limit()` — the attacker can trigger the hashed path unconditionally.

### Recommendation
Apply an advancement-rule-equivalent check to DMQ, analogous to `check_enough_messages_included_advanced` used for HRMP: verify that `full_messages`' cumulative size plus the size of the first hashed message exceeds `messages_collection_size_limit()`, i.e., that hashing was only used when genuinely necessary for PoV constraints. Call this check from `enqueue_inbound_downward_messages` in place of (or in addition to) `check_enough_messages_included_basic`.

### Proof of Concept
Rust integration test in `cumulus/pallets/parachain-system/src/tests.rs` style:
1. Seed a DMQ (via relay sproof builder) with messages `[M1 (small, non-fee), M2 (small, ReceiveTeleportedAsset XCM), M3, M4 (small)]`, all well within `messages_collection_size_limit()`.
2. Construct `InboundMessagesData` manually (bypassing `do_create_inherent`'s honest `into_abridged`) with `full_messages = [M1]` and `hashed_messages = [compressed(M2), compressed(M3), compressed(M4)]`.
3. Submit via `set_validation_data` with `dmq_mqc_head` computed by folding `extend_downward(M1)` then `extend_with_hashed_msg` over `M2..M4` — assert this succeeds (`enqueue_inbound_downward_messages` does not panic).
4. Assert `HANDLED_DMP_MESSAGES` only contains `M1`'s payload (M2's XCM never dispatched via `T::DmpQueue`).
5. Assert `ProcessedDownwardMessages::get() == 4` and `LastDmqMqcHead` matches relay head, proving "processed" state advanced while M2's asset-teleport XCM was silently dropped.
6. Contrast with an equivalent test attempting the same but where HRMP's `check_enough_messages_included_advanced` is invoked — showing that HRMP would reject the analogous manipulation while DMQ accepts it. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1434-1455)
```rust
	///            correspond to the ones found on the relay-chain.
	fn enqueue_inbound_horizontal_messages(
		ingress_channels: &[(ParaId, cumulus_primitives_core::AbridgedHrmpChannel)],
		horizontal_messages: AbridgedInboundHrmpMessages,
		relay_parent_number: relay_chain::BlockNumber,
	) -> Weight {
		let mut mqc_heads = <LastHrmpMqcHeads<T>>::get();
		let (messages, hashed_messages) = horizontal_messages.messages();

		// First, check the HRMP advancement rule.
		let maybe_first_hashed_msg_sender = hashed_messages.first().map(|(sender, _msg)| *sender);
		if let Some(first_hashed_msg_sender) = maybe_first_hashed_msg_sender {
			let channel =
				Self::get_ingress_channel_or_panic(ingress_channels, first_hashed_msg_sender);
			horizontal_messages.check_enough_messages_included_advanced(
				"HRMP",
				AbridgedInboundMessagesSizeInfo {
					max_full_messages_size: Self::messages_collection_size_limit(),
					first_hashed_msg_max_size: channel.max_message_size as usize,
				},
			);
		}
```

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L172-218)
```rust
	/// Check that the current collection contains at least 1 full message if needed.
	pub fn check_enough_messages_included_basic(&self, collection_name: &str) {
		if self.hashed_messages.is_empty() {
			return;
		}

		// Here we just check that there is at least 1 full message.
		assert!(
			self.full_messages.len() >= 1,
			"[{}] Advancement rule violation: full messages missing",
			collection_name,
		);
	}

	/// Check that the current collection contains as many full messages as possible, taking into
	/// consideration the collection constraints.
	///
	/// The `AbridgedInboundMessagesCollection` is provided to the runtime by a collator.
	/// A malicious collator can provide a collection that contains no full messages or fewer
	/// full messages than possible, leading to censorship.
	pub fn check_enough_messages_included_advanced(
		&self,
		collection_name: &str,
		size_info: AbridgedInboundMessagesSizeInfo,
	) {
		// We should check that the collection contains as many full messages as possible
		// without exceeding the max expected size.
		let AbridgedInboundMessagesSizeInfo { max_full_messages_size, first_hashed_msg_max_size } =
			size_info;

		let mut full_messages_size = 0usize;
		for msg in &self.full_messages {
			full_messages_size = full_messages_size.saturating_add(msg.data().len());
		}

		// The worst case scenario is that were the first message that had to be hashed
		// is a max size message.
		assert!(
			full_messages_size.saturating_add(first_hashed_msg_max_size) > max_full_messages_size,
			"[{}] Advancement rule violation: full messages size smaller than expected. \
			full msgs size: {}, first hashed msg max size: {}, max full msgs size: {}",
			collection_name,
			full_messages_size,
			first_hashed_msg_max_size,
			max_full_messages_size
		);
	}
```

**File:** prdoc/stable2603/pr_9086.prdoc (L1-8)
```text
title: Make HRMP advancement rule more restrictive
doc:
- audience: Runtime Dev
  description: |-
    This PR improves `check_enough_messages_included()` and makes the advancement rule more restrictive for HRMP.
crates:
- name: cumulus-pallet-parachain-system
  bump: major
```

**File:** polkadot/runtime/parachains/src/dmp.rs (L300-326)
```rust
	pub fn queue_downward_message(
		config: &HostConfiguration<BlockNumberFor<T>>,
		para: ParaId,
		msg: DownwardMessage,
	) -> Result<(), QueueDownwardMessageError> {
		let serialized_len = msg.len();
		Self::can_queue_downward_message(config, &para, &msg)?;

		let inbound = InboundDownwardQueue::<T>::push_back(para, msg)
			.map_err(|_| QueueDownwardMessageError::ExceedsMaxQueueSize)?;
		let q_len = InboundDownwardQueue::<T>::len(para).unwrap_or(0);

		// obtain the new link in the MQC and update the head.
		DownwardMessageQueueHeads::<T>::mutate(para, |head| {
			let new_head =
				BlakeTwo256::hash_of(&(*head, inbound.sent_at, T::Hashing::hash_of(&inbound.msg)));
			*head = new_head;
		});

		let threshold =
			Self::dmq_max_length(config.max_downward_message_size).saturating_div(THRESHOLD_FACTOR);
		if q_len > threshold as u64 {
			Self::increase_fee_factor(para, serialized_len as u128);
		}

		Ok(())
	}
```
