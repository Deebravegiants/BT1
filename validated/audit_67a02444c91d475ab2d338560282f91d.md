All code references in the claim check out exactly against the actual repository state, and the asymmetry between DMQ and HRMP is confirmed to be intentional per `prdoc/stable2603/pr_9086.prdoc`, which states the advancement rule was tightened "for HRMP" only.

Audit Report

## Title
Malicious collator can permanently censor specific DMP messages by exploiting the weak `check_enough_messages_included_basic` advancement rule used for the DMQ path - ([File: cumulus/pallets/parachain-system/src/parachain_inherent.rs] / [File: cumulus/pallets/parachain-system/src/lib.rs])

## Summary
`enqueue_inbound_downward_messages` validates the collator-submitted DMQ split with `check_enough_messages_included_basic`, which only asserts that at least one full message exists whenever any message is hashed, without verifying that hashing was actually necessary for size reasons. The HRMP path, by contrast, uses the strictly stronger `check_enough_messages_included_advanced`. This asymmetry lets a malicious collator hash an arbitrary, otherwise-fitting DMP message (accompanied by one trivial full message) so it is never dispatched to `T::DmpQueue::handle_messages`, while still being marked as processed via the MQC chain — resulting in permanent, silent censorship of that message.

## Finding Description
`enqueue_inbound_downward_messages` calls `downward_messages.check_enough_messages_included_basic("DMQ")` [1](#0-0) , whose implementation only requires `full_messages.len() >= 1` when `hashed_messages` is non-empty, with no size accounting whatsoever [2](#0-1) . In contrast, `enqueue_inbound_horizontal_messages` applies `check_enough_messages_included_advanced` for HRMP, which asserts that the full-messages byte total plus the worst-case size of the first hashed message must exceed the size limit — i.e., a message may only be hashed when it truly didn't fit [3](#0-2) [4](#0-3) . The doc-comment on `check_enough_messages_included_advanced` explicitly acknowledges the censorship risk this stricter check is designed to prevent [5](#0-4) , and `prdoc/stable2603/pr_9086.prdoc` confirms that this hardening was applied only to HRMP [6](#0-5) .

`into_abridged` — the honest algorithm used by `do_create_inherent` to split messages into full/hashed based on the real size budget — is not enforced on-chain; it's just the default block-authoring helper [7](#0-6) [8](#0-7) . A malicious collator submits `set_validation_data` directly (an unsigned, `ensure_none` call authored solely by the collator) with an arbitrary `full_messages`/`hashed_messages` split [9](#0-8) . The only chain-level guards are (1) the DMQ MQC head hash chain match, which is agnostic to whether a message is represented as full or hashed since both `extend_downward` and `extend_with_hashed_msg` feed the same chain using the correct (public) message hash, and (2) the weak basic check. Once accepted, only `full_messages` are dispatched via `bounded_msgs_iter` to `T::DmpQueue::handle_messages`, while hashed messages only update the MQC head and cause `LastProcessedDownwardMessage` to advance past them — marking them permanently "processed" without ever executing their payload [10](#0-9) . No mechanism was found in the codebase to later recover or re-dispatch a message that was hashed rather than delivered in full — the `HashedMessage` type only stores a hash of the message, with no downstream reconstruction path.

## Impact Explanation
This gives a malicious/colluding collator the ability to selectively and permanently drop any specific DMP message (e.g., governance dispatches, XCM Transact calls, or reserve-transfer completions targeted at the parachain) while producing an inherent that satisfies all on-chain assertions. This is precisely the censorship scenario the code's own documentation warns about for the advanced check, but the mitigation was never extended to the DMQ path. The result is a concrete, permanent loss of message delivery with no error signaled on-chain (no assertion failure), which is a legitimate protocol-level censorship/integrity issue distinct from routine collator equivocation or block-withholding attacks.

## Likelihood Explanation
The attack requires only a single malicious or colluding collator authoring a block for the parachain — a standard part of the threat model, since collators are explicitly treated as untrusted in this code (the DMQ head mismatch check exists precisely to detect misbehaving collators). No relay-chain collusion, privileged keys, or governance access are needed; DMP message contents are public on the relay chain, so the collator can always compute the correct hash for the message it wants to suppress. The attack is repeatable every block for any DMP message of the attacker's choosing.

## Recommendation
Apply `check_enough_messages_included_advanced` (or an equivalent size-based check) to the DMQ path in `enqueue_inbound_downward_messages`, replacing the call to `check_enough_messages_included_basic("DMQ")` with a check verifying that the full-message byte total plus the maximum possible size of the first hashed message exceeds `messages_collection_size_limit()`, matching the guarantee already provided for HRMP.

## Proof of Concept
Extend the existing test module in `parachain_inherent.rs`:
```rust
#[test]
fn dmq_basic_check_allows_censorship_of_large_fitting_message() {
    let small = InboundDownwardMessage { sent_at: 0, msg: vec![1; 1] };
    let large = InboundDownwardMessage { sent_at: 0, msg: vec![1; 900] }; // fits under e.g. 1000-byte budget

    let crafted = AbridgedInboundDownwardMessages {
        full_messages: vec![small.clone()],
        hashed_messages: vec![(&large).into()],
    };

    // Basic check (used for DMQ) passes trivially — accepts unnecessary hashing.
    crafted.check_enough_messages_included_basic("DMQ");

    // Advanced check (used for HRMP) rejects the identical split.
    let result = std::panic::catch_unwind(|| {
        crafted.check_enough_messages_included_advanced(
            "DMQ",
            AbridgedInboundMessagesSizeInfo {
                max_full_messages_size: 1000,
                first_hashed_msg_max_size: 900,
            },
        )
    });
    assert!(result.is_err());
}
```
This demonstrates that the DMQ-applied check (`check_enough_messages_included_basic`) accepts a split that hashes a large, budget-fitting message while the HRMP-applied check (`check_enough_messages_included_advanced`) would reject the identical data, confirming the gap allows silent, permanent censorship of any chosen DMP message via `enqueue_inbound_downward_messages`.

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

**File:** cumulus/pallets/parachain-system/src/lib.rs (L1330-1354)
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

**File:** prdoc/stable2603/pr_9086.prdoc (L1-5)
```text
title: Make HRMP advancement rule more restrictive
doc:
- audience: Runtime Dev
  description: |-
    This PR improves `check_enough_messages_included()` and makes the advancement rule more restrictive for HRMP.
```
