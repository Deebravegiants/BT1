No enforced maximum body size was found for dispatched requests in this index, and the pallet-messaging-incentives mint is uncapped and proportional to raw byte count with no burn/decay counterpart.

### Title
Unbounded reputation-token minting via self-relayed, fee-free request dispatch - (File: modules/pallets/messaging-incentives/src/lib.rs)

### Summary
`pallet-messaging-incentives::on_executed` mints `ReputationAsset` to whichever account signed a delivered `Message::Request` batch, scaled linearly by `bytes × MintPerByte`, with no cap, no cost accounting, and no corresponding burn/decrease path — structurally the same asymmetry as the Flat.money bug: a cheap, freely repeatable action (there, "increase size"; here, "dispatch + self-relay a request") mints a reward with no offsetting mechanism that ever reduces it.

### Finding Description
`Pallet::on_executed` reads `MintPerByte`, computes `bytes = message_bytes(&mw.message)` (sum of `max(body.len(), 32)` over all requests in the message, floored per-request specifically to prevent gaming via splitting), and mints `rate * bytes` of `ReputationAsset` to the account recovered from the message's `signer` field via `relayer_for`. [1](#0-0) 

The byte-counting/floor logic: [2](#0-1) 

There is no requirement that the dispatching app paid any fee proportional to the minted amount — dispatch is fee-free at the runtime layer on Polkadot-SDK chains; only an *optional* relayer fee is attached if the sender wants a third-party relayer, and self-relaying (the same account that dispatches also submits the delivery message and signs it) is not prohibited anywhere in this pallet: [3](#0-2) 

The mint is entirely one-directional: every successfully executed request message with a non-zero recovered signer mints tokens, but there is no path in this pallet (or any adjoining pallet) that removes or offsets previously minted `ReputationAsset` when the underlying "work" is reversed, refunded, or was never economically meaningful (e.g. a zero/near-zero-fee, self-authored, trivially-sized-but-padded request). This mirrors the `LeverageModule.executeAdjust` flaw: minting on a "positive" action with no corresponding decrement on the inverse/negating action, so repeating cheap actions accumulates the reward without bound.

### Impact Explanation
An attacker can dispatch a stream of self-authored `PostRequest`s (any destination module accepting arbitrary bodies, or even one that reverts/no-ops downstream) from any connected chain, pad each request body to whatever size maximizes `bytes × MintPerByte`, then act as their own relayer, sign the `Message::Request` batch, and submit it to `pallet-ismp::execute`. Each successful batch mints `ReputationAsset` proportional to raw bytes to the attacker's own account, with no fee collected on the Polkadot-SDK dispatch side to offset it (only gas/proof-verification cost on the source chain, which is unrelated to the byte-scaled mint rate governance sets). Since `ReputationAsset` is explicitly documented as a reputation/incentive asset feeding collator or governance-adjacent mechanisms (`IncentivesManager`, `pallet-collator-manager` Config bound), unbounded free minting directly undermines whatever weight or privilege that asset confers — economically identical to "mint as many points as you want" in the original report.

### Likelihood Explanation
Reachable by any unprivileged actor able to dispatch an ISMP request and submit a signed delivery message (i.e., act as their own relayer) — no special permission is required beyond `MintPerByte` being governance-set to non-zero, which is the pallet's intended operating state. The per-request 32-byte floor and per-request (not per-envelope) application were deliberately designed to prevent *splitting*-based amplification, but nothing prevents *padding* a single request's body arbitrarily large, nor repeating the whole flow indefinitely at whatever cadence the source chain allows.

### Recommendation
Tie the reputation mint to actual economic cost paid by the dispatching application (e.g., only mint proportional to a non-zero relayer fee actually collected via `FeeMetadata`, or cap the per-account/per-window mint), rather than raw byte count of a self-authored, potentially fee-free message. Consider requiring the delivering relayer to differ from the request's originating account, or rate-limit/decay minted reputation so that unpaid, self-relayed traffic cannot accumulate reputation without bound.

### Proof of Concept
1. Governance sets `MintPerByte::set_mint_per_byte(rate)` to a non-zero value (normal operating configuration). [4](#0-3) 
2. Attacker, from any connected source chain, dispatches a `PostRequest` whose `body` is padded to a large size, to any destination module (the module's `on_accept` outcome is irrelevant to the mint — only successful message *delivery/execution* on the ISMP handler matters).
3. Attacker (or a colluding account) submits the resulting `Message::Request` to `pallet_ismp::Pallet::execute`, signing it with their own sr25519 key so `relayer_for` resolves to their own account.
4. `on_executed` computes `bytes = max(body.len(), 32)` for the request and mints `rate * bytes` `ReputationAsset` to the attacker's account, as confirmed by the pallet's own test `on_executed_mints_accumulate_across_deliveries`, which shows mints accumulate without limit across repeated deliveries. [5](#0-4) 
5. Repeat steps 2–4 indefinitely; each cycle mints more `ReputationAsset` with no burn, cap, or fee-based clawback, at attacker-controlled cadence limited only by source-chain throughput/gas — not by any Hyperbridge-side value paid.

### Citations

**File:** modules/pallets/messaging-incentives/src/lib.rs (L106-113)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(Weight::from_parts(10_000_000, 0).saturating_add(T::DbWeight::get().writes(1)))]
		pub fn set_mint_per_byte(origin: OriginFor<T>, amount: BalanceOf<T>) -> DispatchResult {
			T::AdminOrigin::ensure_origin(origin)?;
			MintPerByte::<T>::put(amount);
			Self::deposit_event(Event::MintRateUpdated { amount });
			Ok(())
		}
```

**File:** modules/pallets/messaging-incentives/src/lib.rs (L121-135)
```rust
	/// Same minimum-byte rule as the bandwidth gate (`max(body, 32)`),
	/// applied **per request** so packing requests into one envelope
	/// vs. splitting them across many produces identical mints.
	/// Applying the floor once per envelope would let a relayer inflate
	/// the mint by splitting (each split picks up its own 32-byte floor).
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

**File:** modules/pallets/messaging-incentives/src/lib.rs (L160-186)
```rust
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

**File:** docs/content/developers/polkadot/fees.mdx (L5-13)
```text
# Hyperbridge Fees

Hyperbridge no longer charges a protocol fee on Polkadot-SDK chains. Dispatching is free at the runtime layer — applications only need to attach an optional **relayer fee** if they want third-party relayers to deliver their messages.

## Relayer Fees

The relayer fee is an optional incentive provided by applications initiating cross-chain transactions. It compensates Hyperbridge's decentralized relayers for delivering messages to the destination chain. Apps that prefer to self-relay can leave the fee at zero.

The fee is collected by `pallet-ismp`'s `IsmpDispatcher` from the configured `Currency` (typically a stablecoin). It's escrowed into the `RELAYER_FEE_ACCOUNT` and paid out to the relayer that delivers the message (or refunded to the payer on timeout).
```

**File:** modules/pallets/testsuite/src/tests/pallet_messaging_incentives.rs (L161-185)
```rust
/// Each `on_executed` call mints to the relayer; the soulbound semantics
/// live in the runtime call filter, not in the mint path, so successive
/// mints to the same account must accumulate normally.
#[test]
fn on_executed_mints_accumulate_across_deliveries() {
	new_test_ext().execute_with(|| {
		let relayer_pair = sr25519::Pair::from_seed(&[11u8; 32]);
		let relayer_account = AccountId32::new(relayer_pair.public().0);
		setup_relayer_and_asset(&relayer_account);

		MessagingRelayerIncentives::set_mint_per_byte(RuntimeOrigin::root(), 1).unwrap();

		let body = vec![0u8; 100];
		MessagingRelayerIncentives::on_executed(
			vec![signed_request(&relayer_pair, body.clone())],
			vec![],
		)
		.unwrap();
		assert_eq!(relayer_balance(&relayer_account), 100);

		MessagingRelayerIncentives::on_executed(vec![signed_request(&relayer_pair, body)], vec![])
			.unwrap();
		assert_eq!(relayer_balance(&relayer_account), 200);
	});
}
```
