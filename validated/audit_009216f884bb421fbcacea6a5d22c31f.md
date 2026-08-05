Audit Report

## Title
Malicious collator can permanently orphan (hash-skip) any suffix of the DMQ — including fee-bearing XCM messages — because DMP lacks the "advancement rule" check that HRMP enforces - ([File: cumulus/pallets/parachain-system/src/lib.rs])

## Summary
`enqueue_inbound_downward_messages` calls only `check_enough_messages_included_basic("DMQ")` on the collator-supplied `AbridgedInboundDownwardMessages`, which merely asserts at least one full message exists whenever any hashed message is present, unlike `enqueue_inbound_horizontal_messages` for HRMP, which additionally calls `check_enough_messages_included_advanced` to verify that hashing was actually necessary given the PoV size budget. This asymmetry lets a malicious collator hash (and thereby permanently orphan, once `ProcessedDownwardMessages` advances) any suffix of the DMQ, including fee-bearing XCM messages, without failing the MQC head assertion, because the hash contribution to the MQC head is identical for "full" and "hashed" categorizations and only depends on order.

## Finding Description
`AbridgedInboundMessagesCollection::check_enough_messages_included_basic` (cumulus/pallets/parachain-system/src/parachain_inherent.rs:173-184) only asserts `full_messages.len() >= 1` when `hashed_messages` is non-empty; it never checks whether the full messages' cumulative size plus the size of the next message actually exceeded `messages_collection_size_limit()`. This is the only rule applied to DMQ data, invoked at cumulus/pallets/parachain-system/src/lib.rs:1323, inside `enqueue_inbound_downward_messages` (lib.rs:1319-1367). By contrast, HRMP additionally invokes `check_enough_messages_included_advanced` (lib.rs:1444-1455, parachain_inherent.rs:192-218), which asserts `full_messages_size + first_hashed_msg_max_size > max_full_messages_size`, closing the gap that PR #9086 (`prdoc/stable2603/pr_9086.prdoc`) explicitly targeted for HRMP ("Make HRMP advancement rule more restrictive").

Both `extend_downward` (for full messages) and `extend_with_hashed_msg` (for hashed messages) fold into the same MQC head using `(sent_at, hash(data))`, so the categorization of a message as "full" vs "hashed" has no bearing on the final MQC head — only the relative order of folding (`full_messages` first, then `hashed_messages`, at lib.rs:1334-1336 and 1345-1351) matters for reproducing `expected_dmq_mqc_head`. This means the boundary between full and hashed messages must correspond to a prefix/suffix split of the true DMQ order, but a collator is otherwise free to choose where that split occurs. Because the basic check is satisfied by a single earlier dummy full message, a collator can place any target message (and everything sent after it) into the hashed suffix regardless of whether the real PoV budget required it.

Once the block is included, `dmq_head.head() == expected_dmq_mqc_head` still holds (lib.rs:1362) because the check is order-preserving and category-agnostic, and `ProcessedDownwardMessages::<T>::put(message_count)` is submitted (lib.rs:1364), which is used to prune the corresponding entries from the relay chain's `DownwardMessageQueueHeads`/`InboundDownwardQueue` (polkadot/runtime/parachains/src/dmp.rs). The hashed messages are never passed into `T::DmpQueue::handle_messages` via `bounded_msgs_iter()` (lib.rs:1354), since `bounded_msgs_iter` only iterates `full_messages` (parachain_inherent.rs:249-260). Their XCM payloads are therefore never dispatched, yet the relay chain considers them processed and prunes them — an irrecoverable loss of that message's effect (e.g., an asset teleport/reserve-transfer XCM never being executed on the destination, while the sender side treated it as delivered).

I confirmed via direct code inspection that this asymmetry between DMP and HRMP checks is real and present exactly as described: `enqueue_inbound_downward_messages` at lib.rs:1319-1367 only calls the basic check, while `enqueue_inbound_horizontal_messages` at lib.rs:1435-1455 additionally invokes the advanced check using channel-specific `max_message_size` (from `AbridgedHrmpChannel`) obtained via `get_ingress_channel_or_panic`. For DMP, there is no per-channel size analog readily available in the same code path, but `Self::messages_collection_size_limit()` (lib.rs:1269-1277) is already used for computing `max_full_messages_size` during `into_abridged` (lib.rs:1294-1295) and could be reused the same way HRMP does, and there's no evident architectural reason DMP could not receive an equivalent advanced check using the DMQ's configured `max_downward_message_size` (visible via relay chain host configuration) as the `first_hashed_msg_max_size` analog. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

## Impact Explanation
A collator is a permissioned-but-untrusted-for-content block author role; it is trusted to relay and order data faithfully, not to selectively censor or destroy specific messages. This flaw allows such a collator to permanently prevent execution of any targeted downward XCM message — including asset-teleport or reserve-transfer messages that credit funds on the destination parachain — while the relay chain's bookkeeping (`ProcessedDownwardMessages`, MQC head, `DownwardMessageQueueHeads` pruning) proceeds as if the message had been fully processed. This matches an in-scope "funds/XCM messages permanently stuck or lost while state advances" impact class, and additionally has a broader collateral effect (all subsequent DMQ messages after the split point are also dropped), which is a stronger DoS than the minimum needed to demonstrate the bug.

## Likelihood Explanation
This requires only a single block authored by a malicious or compromised collator, using ordinary collator privileges (constructing an inherent), with no additional relay-chain-side or governance conditions. The only cross-check (`assert_eq!(dmq_head.head(), expected_dmq_mqc_head)`) is satisfied by construction because the check does not distinguish full vs. hashed categorization at the hash level. It does not require the DMQ to genuinely exceed `messages_collection_size_limit()`; the attacker can invoke the hashed path unconditionally by fabricating the inherent with an early split.

## Recommendation
Apply an advancement-rule-equivalent check to DMQ, mirroring `check_enough_messages_included_advanced` used for HRMP: verify that the full messages' cumulative size plus the size of the first hashed message (bounded by the DMQ's configured maximum downward message size) exceeds `messages_collection_size_limit()`. Invoke this check from `enqueue_inbound_downward_messages` (lib.rs:1319-1367) in place of, or in addition to, `check_enough_messages_included_basic`.

## Proof of Concept
1. Seed a DMQ (via the relay chain sproof builder used in `cumulus/pallets/parachain-system/src/tests.rs`) with messages `[M1 (small), M2 (fee-bearing XCM, e.g. ReceiveTeleportedAsset), M3, M4 (small)]`, all comfortably within `messages_collection_size_limit()`.
2. Construct an `InboundMessagesData`/`AbridgedInboundDownwardMessages` manually with `full_messages = [M1]` and `hashed_messages = [compressed(M2), compressed(M3), compressed(M4)]`, bypassing the honest `into_abridged` split.
3. Compute `dmq_mqc_head` by folding `extend_downward(M1)` then `extend_with_hashed_msg` over `M2..M4`, and submit via `set_validation_data`.
4. Observe that `enqueue_inbound_downward_messages` does not panic (`check_enough_messages_included_basic` passes since `full_messages.len() == 1`), the `assert_eq!` MQC head check passes, and only `M1`'s payload is passed to `T::DmpQueue::handle_messages` — `M2`'s XCM is never dispatched.
5. Observe `ProcessedDownwardMessages::get() == 4` and `LastDmqMqcHead` matching the relay-provided head, demonstrating that the relay chain will prune all four messages as "processed" while `M2`'s XCM effect was silently dropped.
6. Contrast with an analogous manipulation attempted against HRMP messages in the same test harness, showing `check_enough_messages_included_advanced` correctly rejects (panics on) the equivalent split when it does not reflect genuine PoV necessity, confirming the DMP/HRMP asymmetry.

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

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L249-264)
```rust
impl AbridgedInboundDownwardMessages {
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
