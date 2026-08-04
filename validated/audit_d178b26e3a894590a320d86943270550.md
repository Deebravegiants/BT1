### Title
Malicious collator can permanently censor specific DMP messages by exploiting the weak `check_enough_messages_included_basic` advancement rule used for the DMQ path - ([File: cumulus/pallets/parachain-system/src/parachain_inherent.rs] / [File: cumulus/pallets/parachain-system/src/lib.rs])

### Summary
`AbridgedInboundMessagesCollection::check_enough_messages_included_basic` only requires that at least one full message exist whenever any message is hashed; it does not enforce that hashing only happens when a message truly did not fit the size budget. Unlike HRMP (which uses the stricter `check_enough_messages_included_advanced`, see `enqueue_inbound_horizontal_messages` at [1](#0-0) ), the DMQ path unconditionally uses the weak basic check ( [2](#0-1) ), allowing a malicious collator to hash arbitrarily large, otherwise-fitting DMP messages while satisfying the invariant with a trivially small full message elsewhere in the batch.

### Finding Description
`into_abridged` in [3](#0-2)  is only the *honest* algorithm used by the default block-authoring logic in `do_create_inherent` ( [4](#0-3) ). A malicious collator building its own PoV is not constrained to call `into_abridged` at all — it can submit any `InboundMessagesData` (any split between `full_messages`/`hashed_messages`) directly via the `set_validation_data` inherent call ( [5](#0-4) ), which is unsigned (`ensure_none`) and produced exclusively by the collator.

The only two guards on that submitted split are:
1. The DMQ head hash chain must match the relay-chain-derived `expected_dmq_mqc_head` ( [6](#0-5) ). This check is agnostic to which representation (full vs. hashed) is used for each message — `extend_downward` (full) and `extend_with_hashed_msg` (hashed) both feed into the same chain, and a message hashed by the collator uses the real message hash (which the collator can always compute correctly, since DMP messages are public on the relay chain), so the chain still matches regardless of the full/hashed split.
2. `check_enough_messages_included_basic` ( [7](#0-6) ), invoked for DMQ at [8](#0-7) , only asserts `full_messages.len() >= 1` when `hashed_messages` is non-empty — it says nothing about *which* messages must be full or whether the size budget was actually exceeded.

Contrast this with `check_enough_messages_included_advanced` ( [9](#0-8) ), which asserts that the total size of full messages plus the max possible size of the first hashed message must exceed the size limit — i.e., hashing is only legal when it was actually necessary. This stricter check is applied to HRMP ( [1](#0-0) ) but **not** to DMQ, per `prdoc/stable2603/pr_9086.prdoc`, which documents that the advancement rule was strengthened only "for HRMP."

Exploit flow: A malicious collator wants to censor a specific large DMP message `M` (e.g., a governance/XCM message) while it is still within the size budget. It constructs `AbridgedInboundDownwardMessages` where `M` is placed in `hashed_messages` (using its correct hash, matching relay-chain data) and some trivial unrelated 0/1-byte DMP message is placed in `full_messages`. It submits this via `set_validation_data`. The DMQ head assertion passes because the hash chain is faithfully reconstructed. `check_enough_messages_included_basic` passes trivially because `full_messages.len() >= 1`. `M`'s payload is never dispatched to `T::DmpQueue::handle_messages` (only `full_messages` are dispatched, via `bounded_msgs_iter` at [10](#0-9) ), so `M`'s effect never executes; only its hash is committed to `LastDmqMqcHead`, and `M` is treated as "processed" (`LastProcessedDownwardMessage` advances past it, [11](#0-10) ). The message is permanently skipped — there is no re-delivery mechanism for a message that has already been marked processed via the MQC chain.

### Impact Explanation
A malicious/colluding collator can selectively and permanently censor any DMP message (e.g., specific relay-chain-triggered governance calls, XCM Transact messages, or reserve-transfer completions targeting the parachain) while producing an inherent that passes all on-chain checks. This is exactly the "leading to censorship" scenario the code comment on `check_enough_messages_included_advanced` warns about ( [12](#0-11) ), but the mitigation was applied only to HRMP, leaving DMQ exposed.

### Likelihood Explanation
Requires only an unprivileged/malicious collator with the ability to author blocks for the parachain (a normal, expected threat model for parachain security — collators are explicitly called out as untrusted in the code's own comments). No relay-chain collusion or privileged keys are needed; the collator only needs the (public) DMP message data to compute correct hashes. This is fully repeatable every block, for any DMP message the collator wishes to suppress.

### Recommendation
Apply the same strengthened advancement rule (`check_enough_messages_included_advanced`, or an equivalent size-based check) to the DMQ path in `enqueue_inbound_downward_messages`, replacing or supplementing the call to `check_enough_messages_included_basic("DMQ")` at [8](#0-7)  with a check that verifies the full-message byte total plus the max possible size of the first hashed message exceeds `messages_collection_size_limit()`.

### Proof of Concept
Rust unit test (extending the existing test module in `parachain_inherent.rs`):
```rust
#[test]
fn dmq_basic_check_allows_censorship_of_large_fitting_message() {
    // Build a set: [small full msg (1 byte)] + [large hashed msg (fits size budget)]
    let small = InboundDownwardMessage { sent_at: 0, msg: vec![1; 1] };
    let large = InboundDownwardMessage { sent_at: 0, msg: vec![1; 900] }; // would fit under e.g. 1000-byte budget

    let crafted = AbridgedInboundDownwardMessages {
        full_messages: vec![small.clone()],
        hashed_messages: vec![(&large).into()],
    };

    // Basic check (used for DMQ in enqueue_inbound_downward_messages) passes trivially.
    crafted.check_enough_messages_included_basic("DMQ"); // does not panic

    // Advanced check (used for HRMP) would reject this exact split, proving the gap.
    let result = std::panic::catch_unwind(|| {
        crafted.check_enough_messages_included_advanced(
            "DMQ",
            AbridgedInboundMessagesSizeInfo {
                max_full_messages_size: 1000,
                first_hashed_msg_max_size: 900,
            },
        )
    });
    assert!(result.is_err(), "advanced check should reject unnecessary hashing of a fitting message");
}
```
Expected assertions: `check_enough_messages_included_basic` returns without panicking (accepts the crafted split), while `check_enough_messages_included_advanced` panics on the identical data — demonstrating that a collator relying on the DMQ code path (which only enforces the basic check per `enqueue_inbound_downward_messages`) can hash a large, fitting DMP message and have it accepted on-chain, achieving message censorship.

### Citations

**File:** cumulus/pallets/parachain-system/src/lib.rs (L677-682)
```rust
		pub fn set_validation_data(
			origin: OriginFor<T>,
			data: BasicParachainInherentData,
			inbound_messages_data: InboundMessagesData,
		) -> DispatchResult {
			ensure_none(origin)?;
```

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

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1330-1362)
```rust
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
```

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1444-1454)
```rust
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
```

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L122-142)
```rust
	pub fn into_abridged(
		self,
		size_limit: &mut usize,
	) -> AbridgedInboundMessagesCollection<Message> {
		let mut messages = self.messages;

		let mut split_off_pos = messages.len();
		for (idx, message) in messages.iter().enumerate() {
			if *size_limit < message.data().len() {
				break;
			}
			*size_limit -= message.data().len();

			split_off_pos = idx + 1;
		}

		let extra_messages = messages.split_off(split_off_pos);
		let hashed_messages = extra_messages.iter().map(|msg| msg.to_compressed()).collect();

		AbridgedInboundMessagesCollection { full_messages: messages, hashed_messages }
	}
```

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L172-184)
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
```

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L186-191)
```rust
	/// Check that the current collection contains as many full messages as possible, taking into
	/// consideration the collection constraints.
	///
	/// The `AbridgedInboundMessagesCollection` is provided to the runtime by a collator.
	/// A malicious collator can provide a collection that contains no full messages or fewer
	/// full messages than possible, leading to censorship.
```

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L192-218)
```rust
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

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L250-265)
```rust
	/// Returns an iterator over the messages that maps them to `BoundedSlices`.
	pub fn bounded_msgs_iter<MaxMessageLen: Get<u32>>(
		&self,
	) -> impl Iterator<Item = BoundedSlice<'_, u8, MaxMessageLen>> {
		self.full_messages
			.iter()
			// Note: we are not using `.defensive()` here since that prints the whole value to
			// console. In case that the message is too long, this clogs up the log quite badly.
			.filter_map(|m| match BoundedSlice::try_from(&m.msg[..]) {
				Ok(bounded) => Some(bounded),
				Err(_) => {
					defensive!("Inbound Downward message was too long; dropping");
					None
				},
			})
	}
```
