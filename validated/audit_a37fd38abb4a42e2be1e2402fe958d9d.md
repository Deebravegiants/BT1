### Title
Reputation-mint incentive silently pays 0 bytes (no reward) for relayer-delivered Response messages despite `relayer_for` recognizing and crediting the same relayer identity for Requests - ([File: modules/pallets/messaging-incentives/src/lib.rs])

### Summary
`pallet-messaging-incentives` rewards relayers per byte of delivered ISMP payload, but `message_bytes()` only computes a non-zero byte count for `Message::Request`; every other message variant, including `Message::Response`, falls through to the catch-all `_ => 0` arm. Meanwhile `relayer_for()` explicitly supports both `Message::Request` and `Message::Response`, recovering the delivering relayer's account from the signer field for both variants. Because the payout in `on_executed` is `rate.saturating_mul(bytes_balance)`, a relayer who delivers a Response message (e.g. a GET response) always computes `amount == 0` and the mint is skipped, even though the same code path proves it can correctly identify that relayer.

### Finding Description
`on_executed` (the `FeeHandler` implementation consumed by `pallet-ismp` on every processed batch) loops over `messages: Vec<MessageWithWeight>` and, for each message, computes: [1](#0-0) 

`message_bytes` is the source of the byte count used to size the mint: [2](#0-1) 

Only `Message::Request` contributes bytes; `Message::Response` (and any other variant) returns `0`. Since `amount = rate.saturating_mul(bytes_balance)` and `bytes_balance` is `0` for responses, the `if amount.is_zero() { continue; }` guard skips the mint entirely for response deliveries — before `relayer_for` is even consulted.

Yet `relayer_for` is written to support exactly this case: [3](#0-2) 

This asymmetry mirrors the reported bug class: a fee/incentive mechanism (referral fee / UI fee in the original report; reputation-mint incentive here) is wired to recognize and reward one code path (post requests) but a structurally identical path (get responses) that goes through the same relayer-identification logic is left unrewarded due to an incomplete match arm, not an intentional design exclusion (unlike liquidations in the original report, which were explicitly and deliberately excluded).

### Impact Explanation
Relayers who deliver `GetResponse` messages (i.e., service the get-request/response leg of Hyperbridge's cross-chain query flow) receive no reputation-token reward regardless of the configured `MintPerByte` rate, while relayers delivering `PostRequest` messages of identical byte size are rewarded. This is a direct, protocol-level loss of intended incentive revenue for a whole class of relayed traffic. If `pallet-collator-manager` or any downstream governance/selection process weights collator/relayer eligibility or reputation on these minted tokens (the pallet doc says the trait is kept for `pallet-collator-manager`), relayers who exclusively or predominantly service response delivery are structurally under-rewarded relative to their real contribution, which can bias relayer participation away from response delivery over time — an economic/availability risk to the get-request/response leg of Hyperbridge messaging. This is reachable by any relayer submitting a signed batch containing response messages through the normal, unprivileged handler/dispatch path (no admin action required to trigger the underpayment — only `set_mint_per_byte` being non-zero, which is normal governance operation).

### Likelihood Explanation
High likelihood of occurrence in normal operation: any time `MintPerByte` is set to a non-zero value (the pallet's very purpose) and a relayer batch includes a `Message::Response`, the incentive is silently zero. No adversarial action or malicious input is needed — it happens on the ordinary, expected code path for GET-response delivery, which is a first-class supported ISMP message type per `relayer_for`'s own match arms and per the wider protocol's GET-request/response feature. The bug is a straightforward oversight in `message_bytes`'s match arms.

### Recommendation
Extend `message_bytes` to compute a byte count for `Message::Response` (and, if intended, other rewarded variants) analogous to the `Message::Request` branch — e.g., summing (with the same `max(len, 32)` floor) the response payload length(s) inside `req.requests`/response body — so that `relayer_for`'s ability to recover response relayers is actually paired with a non-zero reward, consistent with the per-byte incentive design already applied to requests.

### Proof of Concept
1. Governance calls `set_mint_per_byte(rate)` with `rate > 0` via `Pallet::set_mint_per_byte` (`modules/pallets/messaging-incentives/src/lib.rs:108`).
2. A relayer submits and gets included in a processed batch a `Message::Response` (e.g., a `GetResponse` delivery) signed with a valid sr25519 signature in `signer`.
3. `pallet-ismp` invokes `Pallet::on_executed(messages, events)`.
4. For that message, `Self::message_bytes(&mw.message)` matches the `_ => 0` arm (since it's `Message::Response`, not `Message::Request`), yielding `bytes = 0`.
5. `amount = rate.saturating_mul(0) = 0`; the `if amount.is_zero() { continue; }` guard fires, so `T::ReputationAsset::mint_into` is never called and no `ReputationMinted` event is emitted — confirmed by the existing test `unsigned_message_does_not_mint` in `modules/pallets/testsuite/src/tests/pallet_messaging_incentives.rs:289-308`, which demonstrates the same zero-mint path structure but for a different root cause (bad signature); no equivalent test exists asserting a **valid** `Message::Response` is rewarded, and inspection of `message_bytes` confirms it structurally cannot be, regardless of signature validity.
6. Compare with an equal-size `Message::Request` delivered by the same relayer in the same batch: `message_bytes` sums body length(s) with the 32-byte floor, `amount` is non-zero, and `ReputationMinted` fires — demonstrating the reward asymmetry between the two message kinds despite `relayer_for` treating both identically.

### Citations

**File:** modules/pallets/messaging-incentives/src/lib.rs (L126-135)
```rust
	fn message_bytes(message: &Message) -> u32 {
		match message {
			Message::Request(req) => req
				.requests
				.iter()
				.map(|p| core::cmp::max(p.body.len() as u32, 32))
				.sum::<u32>(),
			_ => 0,
		}
	}
```

**File:** modules/pallets/messaging-incentives/src/lib.rs (L140-153)
```rust
	fn relayer_for(message: &Message) -> Option<T::AccountId> {
		let (signer, signed) = match message {
			Message::Request(msg) =>
				(&msg.signer, sp_io::hashing::keccak_256(&msg.requests.encode())),
			Message::Response(msg) =>
				(&msg.signer, sp_io::hashing::keccak_256(&msg.requests.encode())),
			_ => return None,
		};
		Signature::decode(&mut &signer[..])
			.ok()?
			.verify_and_get_sr25519_pubkey(&signed, None)
			.ok()
			.map(T::AccountId::from)
	}
```

**File:** modules/pallets/messaging-incentives/src/lib.rs (L164-182)
```rust
		let rate = MintPerByte::<T>::get();
		if !rate.is_zero() {
			for mw in &messages {
				let bytes = Self::message_bytes(&mw.message);
				let bytes_balance: BalanceOf<T> = (bytes as u128).saturated_into();
				let amount = rate.saturating_mul(bytes_balance);
				if amount.is_zero() {
					continue;
				}
				if let Some(relayer) = Self::relayer_for(&mw.message) {
					match T::ReputationAsset::mint_into(&relayer, amount) {
						Ok(_) =>
							Self::deposit_event(Event::ReputationMinted { relayer, bytes, amount }),
						Err(err) => log::warn!(
							target: "messaging-incentives",
							"reputation mint failed for {bytes}b: {err:?}",
						),
					}
				}
```
