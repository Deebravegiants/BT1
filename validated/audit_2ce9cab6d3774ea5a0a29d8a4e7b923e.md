Based on my research, I found a strong analog in `pallet-messaging-incentives`.

### Title
Messaging-incentives reward calculation is a silent no-op for delivered Response messages, permanently zeroing relayer rewards - (File: `modules/pallets/messaging-incentives/src/lib.rs`)

### Summary
`pallet-messaging-incentives::Pallet::on_executed` mints per-byte reputation rewards to the relayer who delivered a message, sized by `message_bytes(&mw.message)`. That sizing function only computes a non-zero byte count for `Message::Request`; for every other message variant — critically `Message::Response`, which the same pallet explicitly supports for relayer-signature recovery — it silently returns `0`, exactly mirroring the Beta provider's `exchangeRate()` that always returns `0` and zeroes out performance-based rewards regardless of real work done.

### Finding Description
`message_bytes` is the sole "performance"/work metric feeding the reward formula: [1](#0-0) 

It matches `Message::Request` and sums per-byte counts (with a 32-byte floor), but for `_ => 0` — which includes `Message::Response` — it always returns zero.

Yet the same pallet explicitly recognizes `Message::Response` as a rewardable delivery in `relayer_for`, recovering the relayer's signer from response messages just like it does for requests: [2](#0-1) 

The reward computation in `on_executed` then multiplies the (always-zero-for-responses) byte count by the configured rate: [3](#0-2) 

Because `bytes` is `0` for any delivered `Message::Response`, `amount` is always `0` (`rate.saturating_mul(0) == 0`), the `amount.is_zero()` guard fires, and the mint (and `ReputationMinted` event) is skipped entirely — even though the relayer successfully identified and delivered a real cross-chain response with a real, non-trivial payload (`msg.responses` bytes), exactly as `req.requests` bytes are for requests. This is the same class of bug as the Beta pools issue: a stub/no-op performance metric silently zeroes out a reward path that the surrounding code otherwise treats as first-class (here, evidenced by `relayer_for` handling `Message::Response` explicitly).

### Impact Explanation
Any unprivileged relayer that delivers ISMP `PostResponse`/`GetResponse` messages through `pallet-ismp`'s `on_executed` hook receives zero reputation-asset reward for that work, no matter how large the response payload or how the governance-set `MintPerByte` rate is configured. This breaks the base incentive-accounting invariant that reputation rewards scale with delivered message size for all rewarded message classes, permanently starving relayers who specialize in or predominantly deliver responses (e.g. `GetResponse` flows) of due rewards — a violation of protocol logic causing unbacked/lost incentive accounting, analogous to lost rewards in the source report.

### Likelihood Explanation
High likelihood of triggering: this occurs on every single successful response delivery processed through this `FeeHandler`, with no special conditions required — any relayer submitting response messages through the normal message-execution path is affected deterministically and permanently until the code is fixed.

### Recommendation
Extend `message_bytes` to compute a byte count for `Message::Response` (summing `msg.responses` payload lengths with the same 32-byte floor used for requests) instead of falling through to `0` in the wildcard arm, so response deliveries are rewarded consistently with request deliveries.

### Proof of Concept
1. Governance sets `MintPerByte` to a non-zero rate via `set_mint_per_byte`.
2. A relayer signs and submits a `Message::Response` (e.g., delivering a `GetResponse`/`PostResponse`) through `pallet-ismp`, which is processed by `on_executed`.
3. `Self::relayer_for(&mw.message)` successfully recovers the relayer's account (response case is handled).
4. `Self::message_bytes(&mw.message)` returns `0` because `Message::Response` falls into the `_ => 0` arm.
5. `amount = rate.saturating_mul(0) = 0`; the `if amount.is_zero() { continue; }` guard skips minting — no `ReputationMinted` event, no reward — despite a legitimate, successfully delivered response of nonzero size. [4](#0-3)

### Citations

**File:** modules/pallets/messaging-incentives/src/lib.rs (L126-186)
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

	/// Recover the relayer's account from the sr25519 signature on a
	/// `Message`'s `signer` field. Returns `None` if the message has
	/// no signer (e.g. consensus messages) or the signature is bad.
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
}

impl<T: Config> FeeHandler for Pallet<T>
where
	T::AccountId: From<[u8; 32]>,
{
	fn on_executed(
		messages: Vec<MessageWithWeight>,
		_events: Vec<IsmpEvent>,
	) -> DispatchResultWithPostInfo {
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
			}
		}
		Ok(PostDispatchInfo { actual_weight: None, pays_fee: Pays::No })
	}
```
