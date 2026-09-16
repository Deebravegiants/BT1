### Title
Reputation used for collator selection can be farmed cheaply via self-dispatched, byte-inflated ISMP messages - (File: `modules/pallets/messaging-incentives/src/lib.rs`)

### Summary
`pallet-messaging-incentives` mints a **non-transferable reputation asset** to whoever's signature is recovered from a delivered ISMP `Request`/`Response` message, scaled purely by `max(body_size, 32) * MintPerByte`. This reputation balance is the sole ranking criterion `pallet-collator-manager` uses to select block-producing collators each session. Because dispatching messages through Hyperbridge on Polkadot-SDK chains carries no protocol fee and the relayer fee is optional/zero for self-relayed messages, an attacker who dispatches-and-delivers their own messages (self-relaying between chains/modules they control) can mint large amounts of reputation at negligible cost — precisely the same "repeated cheap action farms an economically-decoupled incentive" pattern described in the reference FlatMoney FMP report.

### Finding Description
The mint amount is computed purely from the delivered message's byte size, with no linkage to real economic cost, message value, or actual "work" performed: [1](#0-0) 

and applied unconditionally on every successful execution batch: [2](#0-1) 

The relayer credited is simply whoever's sr25519 signature is attached to the message — there is no requirement that this account be a distinct, competitive, "first-to-deliver" relayer, nor any staking/registration gate: [3](#0-2) 

Dispatching a message costs nothing at the protocol layer on Polkadot-SDK chains, and the relayer fee attached to a dispatch is optional and can be zero for self-relaying: [4](#0-3) 

This reputation asset is then the *only* input to collator (block producer) selection: `pallet-collator-manager::new_session` ranks controllers purely by `ReputationAsset` balance and promotes the top holders to the active collator set: [5](#0-4) 

There is no floor tying the mint rate to genuine economic cost (beyond the trivial 32-byte anti-zero-cost floor), no per-account rate limit, no cooldown between message deliveries, and no requirement that the delivered request/response represent value to any third party. An attacker who runs their own module/contract pair as `from`/`to` on two chains connected to Hyperbridge (or reuses an existing permissionless module) can:
1. Dispatch a `PostRequest` with a large, arbitrary-content body (fee = 0, self-relay) from a source chain they cheaply control.
2. Relay the consensus proof + request message into Hyperbridge themselves, signing with their own controller key.
3. Collect `bytes × MintPerByte` reputation on `on_executed`, repeated as many times as they can afford dispatch/relay gas — exactly analogous to Bob's repeated open/close cycle in the referenced report, where the reward (FMP there, reputation here) is proportional to a self-chosen parameter (`additionalSize` there, `body_size` here) rather than genuine value delivered.

Because reputation directly buys a controller a seat as an active Hyperbridge collator (block producer, with treasury rewards and fisherman/veto duties), this farming primitive is a path to influencing block production with disproportionately low cost relative to the "proven economic activity" the mechanism is designed to require, as stated in the design docs: [6](#0-5) 

### Impact Explanation
Reputation earned this way is fungible with reputation earned by "legitimate" consensus/messaging relayers and BEEFY provers for the purposes of collator ranking. An attacker cheaply inflating their own reputation balance can outrank genuine, economically-productive relayers/provers for collator slots, i.e., an unauthorized/undeserved acquisition of a privileged network role (block authoring, treasury reward collection, and fisherman veto authority over L2 state commitments) that the reputation system is explicitly designed to gate behind real, costly network contribution.

### Likelihood Explanation
Any account can dispatch an ISMP request with an attacker-chosen body size and, if self-relaying (fee = 0) is permitted, deliver it and sign it themselves, with no minimum economic value requirement enforced by `on_executed`. The only "cost" is the raw transaction/gas cost of dispatch + delivery on both ends, which is decoupled from the byte-proportional reward, mirroring the report's core "repeatable, cheap round-trip farms an incentive whose size is chosen by the attacker" pattern.

### Recommendation
Tie the reputation mint to a value that an attacker cannot cheaply and unilaterally inflate — e.g., require a non-zero relayer/dispatch fee proportional to (or exceeding) the reputation payout, cap the mint per source/destination pair or per account per session, introduce a minimum time/interval between rewarded deliveries from the same signer, or require distinct-sender/distinct-relayer attribution so self-dispatched-and-self-relayed traffic cannot earn the same reputation as competitively-won third-party relaying.

### Proof of Concept
1. Attacker controls (or uses permissionlessly) a module pair `(from, to)` on two Hyperbridge-connected chains.
2. Attacker calls `IsmpDispatcher::dispatch_request` with `FeeMetadata { fee: 0, payer: attacker }` and a large `body` (e.g., padded to the max allowed request size).
3. Attacker (as their own relayer) submits the consensus proof + message to Hyperbridge, signing with their controller's sr25519 key, triggering `pallet_ismp` → `pallet_messaging_incentives::on_executed`.
4. `Self::message_bytes` returns the full padded body length; `MintPerByte` × bytes is minted to the attacker's controller account per `on_executed` at `modules/pallets/messaging-incentives/src/lib.rs:160-186`.
5. Repeat steps 2–4 across many self-dispatched messages/sessions; the accumulated `ReputationAsset` balance is compared against genuine operators in `pallet-collator-manager::new_session` (`modules/pallets/collator-manager/src/lib.rs:514-527`), letting the attacker outrank them for a collator seat at a fraction of the intended cost.

### Citations

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

**File:** docs/content/developers/polkadot/fees.mdx (L7-13)
```text
Hyperbridge no longer charges a protocol fee on Polkadot-SDK chains. Dispatching is free at the runtime layer — applications only need to attach an optional **relayer fee** if they want third-party relayers to deliver their messages.

## Relayer Fees

The relayer fee is an optional incentive provided by applications initiating cross-chain transactions. It compensates Hyperbridge's decentralized relayers for delivering messages to the destination chain. Apps that prefer to self-relay can leave the fee at zero.

The fee is collected by `pallet-ismp`'s `IsmpDispatcher` from the configured `Currency` (typically a stablecoin). It's escrowed into the `RELAYER_FEE_ACCOUNT` and paid out to the relayer that delivers the message (or refunded to the payer on timeout).
```

**File:** modules/pallets/collator-manager/src/lib.rs (L514-527)
```rust
			let mut candidates = pallet_collator_selection::CandidateList::<T>::get()
				.into_iter()
				.map(|info| info.who)
				.filter(|stash_account| !Unbonding::<T>::contains_key(stash_account))
				.filter_map(|stash_account| Controller::<T>::get(&stash_account))
				.filter(|controller_account| {
					!RemovedValidators::<T>::contains_key(controller_account) &&
						pallet_session::NextKeys::<T>::get(controller_account.clone().into())
							.is_some()
				})
				.map(|controller_account| {
					(T::ReputationAsset::balance(&controller_account), controller_account)
				})
				.collect::<Vec<_>>();
```

**File:** docs/content/developers/network/collator.mdx (L42-46)
```text
- **Messaging Relayers** deliver cross-chain messages between connected chains and earn `$BRIDGE` rewards through `pallet-messaging-incentives`.
- **Consensus Relayers** submit consensus proofs for connected chains (e.g. Ethereum, BSC) and earn `$BRIDGE` rewards through `pallet-consensus-incentives`.
- **BEEFY Provers** generate and submit BEEFY consensus proofs that attest to the finality of Hyperbridge's own parachain state, earning `$BRIDGE` rewards through `pallet-beefy-consensus-proofs`.

All three roles earn reputation on equal footing. The Collator set is exclusively selected from the pool of operators who have accrued reputation through any combination of these activities. This creates a meritocratic system where the most dedicated and effective network participants are promoted to roles with greater responsibility and rewards.
```
