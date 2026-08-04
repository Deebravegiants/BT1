### Title
Malicious collator can permanently drop DMP messages by over-hashing them past `LastProcessedDownwardMessage`, despite valid MQC accounting - ([File: cumulus/pallets/parachain-system/src/lib.rs])

### Summary
`enqueue_inbound_downward_messages` only calls `check_enough_messages_included_basic` on the collator-supplied `AbridgedInboundDownwardMessages`, which merely requires "at least one full message present if any message is hashed." Unlike the HRMP path, which enforces `check_enough_messages_included_advanced` (verifying the full-message payload actually fills the size budget before hashing is allowed), DMP has no such check, so a collator can hash away real DMP messages that were never dispatched to `T::DmpQueue`, while `LastProcessedDownwardMessage` still advances past them and the DMQ MQC assertion still passes.

### Finding Description
`Pallet::do_create_inherent` ( [1](#0-0) ) is only a client-side helper that produces the `Call::set_validation_data { .. inbound_messages_data }` inherent; the actual `AbridgedInboundDownwardMessages` that ends up on-chain is whatever the collator includes in the block's inherent, so its full/hashed split is fully attacker (collator) controlled at execution time, not enforced to match `messages_collection_size_limit()`.

On-chain, `enqueue_inbound_downward_messages` validates the collection with only the basic rule: [2](#0-1) 

Compare this with the HRMP path which additionally enforces the "advancement rule" that full messages must fill up the size budget before any hashing is allowed: [3](#0-2) [4](#0-3) 

Because `MessageQueueChain::extend_with_hashed_msg`/`extend_downward` compute the exact same hash regardless of whether the message was submitted in full or as a hash-only `HashedMessage` ( [5](#0-4) ), a collator can correctly reconstruct the expected DMQ MQC head using only the hashes of real messages, without ever putting their literal payload in the block, and the final assertion still succeeds: [6](#0-5) 

The `LastProcessedDownwardMessage` pointer is advanced using `reverse_idx`, incrementing once per hashed message that shares `sent_at` with the last literal message: [7](#0-6) 

If the collator submits only 1 literal message with `sent_at = N` followed by many hashed messages that also have `sent_at = N` (a legitimate scenario since many DMP messages can share the same relay block), `reverse_idx` will keep incrementing for every one of them, marking the pointer as having advanced past all of them — even though `T::DmpQueue::handle_messages(downward_messages.bounded_msgs_iter())` was only called with the single literal message, i.e. none of the hashed messages' payload was dispatched: [8](#0-7) 

On the next block, `Pallet::do_create_inherent` calls `drop_processed_messages(&last_processed_msg)` on the fresh DMQ contents, which walks back exactly `reverse_idx` positions from the last message with matching `sent_at` and drains everything up to and including that index: [9](#0-8) 

Since the pointer was advanced past the never-dispatched messages, they are permanently discarded from the collection before they ever get a chance to be re-included as literal messages in a future block. The `check_enough_messages_included_basic` check does not detect this, since it only requires ≥1 full message, not that the correct amount was included.

### Impact Explanation
Any DMP message (including XCM messages carrying asset teleports/transfers destined for a victim account) that a malicious collator chooses to "hash away" alongside a genuine literal message sharing the same `sent_at` is permanently dropped: it is never handed to `T::DmpQueue::handle_messages`, and `LastProcessedDownwardMessage`/`drop_processed_messages` ensure it can never be resubmitted as a literal message in any subsequent block, all while the relay chain's DMQ MQC head check on-chain still succeeds. This can silently and permanently freeze user funds/messages sent via DMP without any observable protocol violation (no panic, no MQC mismatch).

### Likelihood Explanation
This requires only an unprivileged/faulty collator producing blocks for the affected parachain — no root, no leaked keys, no governance action. It is fully reproducible: the attacker only needs at least 2 DMP messages queued for the same relay block (`sent_at`), which is trivial to arrange (e.g., two users sending XCM transfers via the relay chain in the same relay block, or a single large batch), and the collator crafts the inherent's `AbridgedInboundDownwardMessages` to include only 1 of them literally and hash the rest.

### Recommendation
Apply the same "advancement rule" enforcement used for HRMP (`check_enough_messages_included_advanced`) to the DMP path in `enqueue_inbound_downward_messages`, i.e., verify that the literal (full) DMP messages included by the collator fill up `messages_collection_size_limit()` as much as possible (using `MaxDmpMessageLenOf<T>` as the worst-case next message size) before allowing any hashing, so a collator cannot hash messages that should have been included in full.

### Proof of Concept
Extend `inherent_messages_are_compressed` in `cumulus/pallets/parachain-system/src/tests.rs`:
1. Construct two DMP messages with the same `sent_at` (e.g., `sent_at = 1`), where the combined size just fits `messages_collection_size_limit()` such that both could legitimately be sent literally.
2. Manually craft the on-chain inherent's `AbridgedInboundDownwardMessages` (bypassing `do_create_inherent`'s "natural" size-based split) to mark the first message literal and the second (smaller/fitting) message as hashed, using its correct hash so the DMQ MQC assertion still passes.
3. Execute the block and assert:
   - `HANDLED_DMP_MESSAGES` only contains the first message's payload (the second's payload was never dispatched to `T::DmpQueue`).
   - `LastProcessedDownwardMessage::<Test>::get()` has advanced with `reverse_idx = 1`, i.e., past the second (undelivered) message.
4. Build the next block reusing the same original DMQ contents (both messages still present in the "relay chain queue"); assert that `drop_processed_messages` drops the second message's data before it is ever again presented to the runtime, and that it never appears in `HANDLED_DMP_MESSAGES` in any later block — proving permanent, silent loss of a valid DMP message despite correct MQC head verification.

### Citations

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1284-1308)
```rust
	fn do_create_inherent(data: ParachainInherentData) -> Call<T> {
		let (data, mut downward_messages, mut horizontal_messages) =
			deconstruct_parachain_inherent_data(data);
		let last_relay_block_number = LastRelayChainBlockNumber::<T>::get();

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

		let inbound_messages_data =
			InboundMessagesData::new(downward_messages, horizontal_messages);

		Call::set_validation_data { data, inbound_messages_data }
	}
```

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1319-1323)
```rust
	fn enqueue_inbound_downward_messages(
		expected_dmq_mqc_head: relay_chain::Hash,
		downward_messages: AbridgedInboundDownwardMessages,
	) -> Weight {
		downward_messages.check_enough_messages_included_basic("DMQ");
```

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1343-1352)
```rust
			let mut last_processed_msg =
				InboundMessageId { sent_at: last_msg.sent_at, reverse_idx: 0 };
			for msg in hashed_messages {
				dmq_head.extend_with_hashed_msg(msg);

				if msg.sent_at == last_processed_msg.sent_at {
					last_processed_msg.reverse_idx += 1;
				}
			}
			LastProcessedDownwardMessage::<T>::put(last_processed_msg);
```

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1354-1354)
```rust
			T::DmpQueue::handle_messages(downward_messages.bounded_msgs_iter());
```

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1357-1362)
```rust
		// After hashing each message in the message queue chain submitted by the collator, we
		// should arrive to the MQC head provided by the relay chain.
		//
		// A mismatch means that at least some of the submitted messages were altered, omitted or
		// added improperly.
		assert_eq!(dmq_head.head(), expected_dmq_mqc_head, "DMQ head mismatch");
```

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1443-1455)
```rust
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

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L94-115)
```rust
	/// Drop all the messages up to `last_processed_msg`.
	pub fn drop_processed_messages(&mut self, last_processed_msg: &InboundMessageId) {
		let mut last_processed_msg_idx = None;
		let messages = &mut self.messages;
		for (idx, message) in messages.iter().enumerate().rev() {
			let sent_at = message.sent_at();
			if sent_at == last_processed_msg.sent_at {
				last_processed_msg_idx = idx.checked_sub(last_processed_msg.reverse_idx as usize);
				break;
			}
			// If we build on the same relay parent twice, we will receive the same messages again
			// while `last_processed_msg` may have been increased. We need this check to make sure
			// that the old messages are dropped.
			if sent_at < last_processed_msg.sent_at {
				last_processed_msg_idx = Some(idx);
				break;
			}
		}
		if let Some(last_processed_msg_idx) = last_processed_msg_idx {
			messages.drain(..=last_processed_msg_idx);
		}
	}
```

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L186-218)
```rust
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

**File:** cumulus/primitives/parachain-inherent/src/lib.rs (L214-231)
```rust
	/// Extend the hash chain with a `HashedMessage`.
	pub fn extend_with_hashed_msg(&mut self, hashed_msg: &HashedMessage) -> &mut Self {
		let prev_head = self.0;
		self.0 = BlakeTwo256::hash_of(&(prev_head, hashed_msg.sent_at, &hashed_msg.msg_hash));
		self
	}

	/// Extend the hash chain with an HRMP message. This method should be used only when
	/// this chain is tracking HRMP.
	pub fn extend_hrmp(&mut self, horizontal_message: &InboundHrmpMessage) -> &mut Self {
		self.extend_with_hashed_msg(&horizontal_message.into())
	}

	/// Extend the hash chain with a downward message. This method should be used only when
	/// this chain is tracking DMP.
	pub fn extend_downward(&mut self, downward_message: &InboundDownwardMessage) -> &mut Self {
		self.extend_with_hashed_msg(&downward_message.into())
	}
```
