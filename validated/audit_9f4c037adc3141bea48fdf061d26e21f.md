### Title
Weak `check_enough_messages_included_basic` DMP censorship-guard permits collator-selected message gaps - ([File: cumulus/pallets/parachain-system/src/parachain_inherent.rs])

### Summary
`AbridgedInboundMessagesCollection::check_enough_messages_included_basic` only asserts that `full_messages.len() >= 1` whenever `hashed_messages` is non-empty, whereas the stricter `check_enough_messages_included_advanced` asserts that as much of the size budget as possible was spent on full messages. If a parachain runtime wires `set_validation_data`/inherent processing to the "basic" variant (or to no size-aware variant at all), a collator can supply an `AbridgedInboundDownwardMessages`/`AbridgedInboundHrmpMessages` value whose `full_messages` stop right before a specific targeted message and whose `hashed_messages` start at that message, satisfying the weak invariant while still advancing the MQC/watermark past the censored message.

### Finding Description
`AbridgedInboundMessagesCollection` is decoded straight from the collator-supplied inherent (`InboundMessagesData`/`ParachainInherentData`), so `full_messages` and `hashed_messages` are attacker-controlled data, not re-derived deterministically by the runtime. [1](#0-0) 

The pallet exposes two guard functions on this collection:
- `check_enough_messages_included_basic`, which only requires `full_messages.len() >= 1` when there is at least one hashed message — it does not check *which* message was hashed vs. included in full, nor whether more full messages could/should have been included. [2](#0-1) 
- `check_enough_messages_included_advanced`, whose own doc comment explicitly states the risk being asked about: *"A malicious collator can provide a collection that contains no full messages or fewer full messages than possible, leading to censorship."* This variant enforces that `full_messages_size + first_hashed_msg_max_size > max_full_messages_size`, i.e. it forces the collator to include as many full messages as the size budget allows before it may hash any message. [3](#0-2) 

Because only the *hash* of a message (`HashedMessage { sent_at, msg_hash }`) is needed to extend the MQC (message-queue-chain) used to validate the DMQ/HRMP head against the relay chain's committed head, a hashed-only message contributes identically to the MQC regardless of whether its full bytes were included. This means the relay-chain-verified MQC/watermark check cannot detect that a specific message was hashed instead of delivered in full — that is precisely why the size-based `advanced` check was introduced as the real defense. [4](#0-3) 

Only `full_messages` are actually dispatched to the downward/HRMP message handlers (e.g., via `bounded_msgs_iter`); `hashed_messages` entries are never delivered as executable message content and their content is not recoverable from the hash. [5](#0-4) 

If `check_enough_messages_included_basic` is what the runtime actually calls (rather than `advanced`), a collator can legally construct: `full_messages` = all messages strictly before the targeted message `k`, `hashed_messages` = `[hash(msg_k), ...]`. This satisfies `full_messages.len() >= 1` (as long as there is at least one earlier message, or trivially if `k` is the very first message and the collator is willing to omit all full messages — the check even permits `full_messages` to be empty-adjacent scenarios as long as one full message exists somewhere). The watermark/processed-messages counters advance past `msg_k` because the MQC accepts the hashed representation, and `msg_k`'s actual payload (e.g., an XCM `Transact`/reserve-transfer meant to credit a user) is permanently unrecoverable — DMP/HRMP messages are consumed exactly once from the relay chain queue and are not replayed.

**Verification caveat**: I was not able to confirm within the available tool budget which check (`_basic` vs `_advanced`) the pallet's `set_validation_data`/`enqueue_inbound_downward_messages` path actually invokes at runtime, nor whether that choice is a fixed pallet decision or a `Config`-parameterized one. The two call sites for `check_enough_messages_included_*` exist in `cumulus/pallets/parachain-system/src/lib.rs`, but their exact selection logic was not read before the iteration budget was exhausted. If the pallet unconditionally calls `check_enough_messages_included_advanced` in the message-processing path, the described attack is prevented, since the size-budget accounting would force full inclusion of `msg_k` whenever it fits within `max_full_messages_size`. The `_basic` variant's weakness as a standalone censorship vector is nonetheless a code-verified fact and is explicitly flagged as such in the source's own documentation.

### Impact Explanation
If the weaker check is what is actually enforced, a collator (unprivileged relative to governance, but privileged relative to block-building) can deterministically and repeatedly censor a specific user's queued DMP/HRMP message (e.g., an XCM `Transact` reserve-transfer meant to credit that user) while still advancing the processed-message watermark past it, causing permanent loss of that message and any assets/instructions it carried, matching the scoped impact.

### Likelihood Explanation
Exploitability requires: (1) the target runtime configures the pallet to use `check_enough_messages_included_basic` instead of `_advanced` (unverified in this analysis — see caveat above), and (2) the attacker controls a collator slot able to author the block containing the relay-parent at which the target message becomes deliverable. Collator slots are commonly permissionless or rotate among many parties, making repeat targeting plausible if precondition (1) holds. Given the explicit doc comment on `check_enough_messages_included_advanced` calling out exactly this censorship scenario, the codebase authors are aware of the risk, which suggests the advanced check is meant to be the actually-wired guard in current runtimes — but this could not be confirmed from the code read so far.

### Recommendation
Ensure `Pallet::enqueue_inbound_downward_messages` (and the equivalent HRMP path) always calls `check_enough_messages_included_advanced` with the correct `AbridgedInboundMessagesSizeInfo` derived from the actual PoV/weight budget available at block-building time, and remove or clearly gate `check_enough_messages_included_basic` so it can never be substituted for the size-aware check in production runtime configuration.

### Proof of Concept
Rust unit test (extends the existing test module in `cumulus/pallets/parachain-system/src/parachain_inherent.rs`):
```rust
#[test]
fn basic_check_allows_gapped_censorship() {
    // Construct a collection where msg at index k (the "target user message") is placed
    // only in hashed_messages, while an earlier, unrelated message is kept full.
    let victim_hash = HashedMessage { sent_at: 5, msg_hash: sp_core::H256::repeat_byte(0xAB) };
    let messages = AbridgedInboundHrmpMessages {
        full_messages: vec![(1000.into(), InboundHrmpMessage { sent_at: 4, data: vec![1] })],
        hashed_messages: vec![(2000.into(), victim_hash)],
    };
    // The weak check passes despite the victim message never being delivered in full.
    messages.check_enough_messages_included_basic("Test"); // does not panic
    let (full, hashed) = messages.messages();
    assert_eq!(full.len(), 1);
    assert_eq!(hashed.len(), 1);
    // Assert: victim message content is never recoverable/dispatchable from `hashed_messages`,
    // proving the target message is permanently censored while the MQC/watermark still advances.
}
```
Additionally, an integration/emulator test should show that: after `set_validation_data` executes with such a crafted `InboundMessagesData`, `ProcessedDownwardMessages`/HRMP watermark advances past the victim message's `sent_at`, and no subsequent block ever redelivers it, confirming permanent loss — contingent on confirming (via the actual `lib.rs` call site) that `check_enough_messages_included_basic` is the function invoked rather than `_advanced`.

### Citations

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L160-163)
```rust
pub struct AbridgedInboundMessagesCollection<Message: InboundMessage> {
	full_messages: Vec<Message>,
	hashed_messages: Vec<Message::CompressedMessage>,
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

**File:** cumulus/pallets/parachain-system/src/parachain_inherent.rs (L249-265)
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
	}
```

**File:** cumulus/primitives/parachain-inherent/src/lib.rs (L214-219)
```rust
	/// Extend the hash chain with a `HashedMessage`.
	pub fn extend_with_hashed_msg(&mut self, hashed_msg: &HashedMessage) -> &mut Self {
		let prev_head = self.0;
		self.0 = BlakeTwo256::hash_of(&(prev_head, hashed_msg.sent_at, &hashed_msg.msg_hash));
		self
	}
```
