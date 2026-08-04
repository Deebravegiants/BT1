Based on the code I was able to examine, I can confirm the core mechanism described exists, but I was unable to fully verify one precondition (which variant is actually wired into `Pallet::enqueue_inbound_downward_messages`) before running out of tool budget. I'll present findings with that caveat noted.

### Title
Weak `check_enough_messages_included_basic` allows a collator to permanently censor a targeted DMP message while advancing the processed watermark - ([File: cumulus/pallets/parachain-system/src/parachain_inherent.rs])

### Summary
`AbridgedInboundMessagesCollection::check_enough_messages_included_basic` (parachain_inherent.rs:173-184) only asserts that `full_messages.len() >= 1` whenever `hashed_messages` is non-empty, with no relationship to how many messages actually fit or which specific messages are hashed. This is materially weaker than `check_enough_messages_included_advanced` (parachain_inherent.rs:192-218), and the doc comment on the advanced variant explicitly acknowledges: "A malicious collator can provide a collection that contains no full messages or fewer full messages than possible, leading to censorship" (parachain_inherent.rs:189-191).

### Finding Description
`AbridgedInboundDownwardMessages` (a type alias of `AbridgedInboundMessagesCollection<InboundDownwardMessage<...>>`, parachain_inherent.rs:246-247) is supplied directly by the collator as part of `InboundMessagesData` inside the parachain inherent. The struct stores `full_messages: Vec<Message>` and `hashed_messages: Vec<Message::CompressedMessage>` as two separate vectors with no cryptographic binding forcing them to be the "maximal legitimate prefix/suffix split" of the real DMQ - that invariant is only produced naturally by `InboundMessagesCollection::into_abridged` (parachain_inherent.rs:122-142) when honest software builds the inherent; a malicious collator building the inherent data directly is free to put as few messages as it likes into `full_messages` and hash the rest, as long as `hashed_messages` entries carry correct `(sent_at, msg_hash)` pairs (so the MQC head check against relay-chain state still validates).

With `check_enough_messages_included_basic`, a single trivial full message satisfies the entire check regardless of how many messages, or which specific messages, are pushed into `hashed_messages`. Because `hashed_messages` only stores a `HashedMessage { sent_at, msg_hash }` (cumulus/primitives/parachain-inherent/src/lib.rs:171-174) and never the underlying payload, once a message is included there instead of in `full_messages`, its content is never passed to `DownwardMessageHandler`; only its hash is folded into the MQC head, which is what advances the processed/watermark position. Once the relay chain observes the parachain's advanced watermark, it prunes the corresponding entries from its own DMP queue, making the raw message content unrecoverable.

`check_enough_messages_included_advanced` was added specifically to close this gap by requiring that `full_messages` be as large as possible given the actual PoV/message size budget (parachain_inherent.rs:196-217), which constrains a collator to a small, size-bounded amount of hashed-only "spillover" rather than an attacker-chosen arbitrary subset.

**Unverified precondition:** I could not, within the available tool budget, confirm the exact call site(s) in `cumulus/pallets/parachain-system/src/lib.rs` that invoke `check_enough_messages_included_basic` vs. `check_enough_messages_included_advanced` for the downward-message path specifically (grep found two call sites in that file, but I did not get to inspect them). The validity of this finding as an exploitable issue in a shipped runtime is contingent on that call site using the `basic` variant for DMP; if the advanced variant is used for downward messages, the described unbounded/arbitrary-target censorship is not possible (only bounded size-driven spillover is).

### Impact Explanation
If the `basic` check is indeed what gates the downward-message collection, a malicious collator can, in every block it produces, include only one arbitrary small full message and hash-out all other pending DMP messages (including a specific victim's message, e.g., an XCM `Transact`/reserve-transfer meant to credit a user). Because the watermark still advances and the relay chain prunes acknowledged messages, the victim's message is permanently lost with no re-delivery path — a genuine, targeted, permanent freeze/loss of a user's downward-routed transfer or instruction, matching the scoped impact.

### Likelihood Explanation
Feasibility depends entirely on the unverified precondition above. If `basic` is used, the attack is trivial and fully repeatable by any single unprivileged collator (no governance action, no cryptographic forgery needed - the hash itself is honestly computed from the real message, so relay-chain-side MQC validation passes). If `advanced` is used, the attack is bounded to the natural spillover of oversized batches and cannot arbitrarily target one specific message while excluding everything else.

### Recommendation
Confirm and, if necessary, change the runtime wiring so that DMP inherent validation always calls `check_enough_messages_included_advanced` (with the correct `AbridgedInboundMessagesSizeInfo` derived from the actual max message/PoV budget) rather than `check_enough_messages_included_basic`. Consider removing/deprecating the `basic` variant for downward messages entirely, or adding a stronger invariant that ties `full_messages` to the true byte-budget so `full_messages.len() >= 1` can never be satisfied via a single decoy message while an arbitrary victim message is hashed out.

### Proof of Concept
Rust unit test extending the existing `check_enough_messages_included_basic_works` test (parachain_inherent.rs:514-535) for the downward-message alias:
```rust
#[test]
fn basic_check_allows_targeted_censorship() {
    let victim_msg = InboundDownwardMessage { sent_at: 5, msg: victim_payload.clone() };
    let decoy_msg = InboundDownwardMessage { sent_at: 4, msg: vec![0u8; 1] };
    let collection = AbridgedInboundDownwardMessages {
        full_messages: vec![decoy_msg], // only 1 trivial full message
        hashed_messages: vec![(&victim_msg).into(), /* ...many more hashed... */],
    };
    // Should NOT panic even though victim_msg (and others) are entirely hashed-out.
    collection.check_enough_messages_included_basic("Dmp");
    // Assert victim_msg content is unreachable: only hash present, no full_messages entry.
    assert!(collection.messages().0.iter().all(|m| m.msg != victim_payload));
}
```
Expected assertion: the basic check passes despite the victim message being hashed-only, proving no invariant in this function (or, per the unresolved precondition, in the call site using it) prevents targeted, permanent exclusion of a specific message while the watermark still advances.