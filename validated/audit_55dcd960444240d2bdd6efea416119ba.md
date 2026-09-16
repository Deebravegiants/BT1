### Title
Consensus-incentives batch reward attributes all `StateMachineUpdated` events in a `handle_unsigned` batch to the first message's relayer signature, letting an attacker front-run other relayers' consensus proofs into their own batch to steal their rewards - ([File: modules/pallets/consensus-incentives/src/impls.rs])

### Summary
`pallet-consensus-incentives::on_executed` (the `FeeHandler` invoked from `pallet_ismp::execute` for every `handle_unsigned` batch) derives the reward recipient once, from `messages[0]`, and then pays that single relayer for *every* `StateMachineUpdated` event produced anywhere in the batch — including events produced by other `Message::Consensus` entries later in the same batch that were signed by a different relayer.

### Finding Description
`Pallet::execute` in `modules/pallets/ismp/src/impls.rs` runs `handle_incoming_message` over the whole `Vec<Message>` submitted to the permissionless, unsigned `handle_unsigned` extrinsic, collects all resulting events, and calls `T::FeeHandler::on_executed(messages_with_weights, events)` once for the entire batch: [1](#0-0) 

`pallet_ismp::Call::handle_unsigned` is unsigned and permissionless — "Execute the provided batch of ISMP messages for free with valid proofs": [2](#0-1) 

`FeeHandler::on_executed` in `pallet-consensus-incentives` only inspects `messages.get(0)`, verifying that first message's `Signature` over its own `consensus_proof`, and treats the recovered account as *the* relayer for the whole batch: [3](#0-2) 

It then collapses **every** `StateMachineUpdated` event in `events` (not just events attributable to `messages[0]`) by `state_machine_id` and pays `relayer_account` (the signer of `messages[0]`) for each one: [4](#0-3) 

The `signer` field on a `ConsensusMessage` is a genuine sr25519 signature over `keccak_256(consensus_proof)` — it authenticates "who submitted/authorized this specific proof," not "who is entitled to all rewards in this transaction." Because `handle_unsigned` accepts an arbitrary `Vec<Message>` and consensus messages/proofs observed in the public transaction pool are not bound to any particular submitter (proofs and relayer signatures are just data, freely copyable), any unprivileged party can:
1. Observe RelayerB's pending, validly-signed `Message::Consensus` update for state machine `B` (or any already-broadcast but not-yet-included proof) in the mempool.
2. Craft their own `handle_unsigned` batch with **their own** signed consensus message for state machine `A` placed first, followed by RelayerB's copied consensus message for `B` as a later entry.
3. Submit this combined batch (front-running RelayerB's own submission).

Both consensus updates verify successfully (they carry valid, real state-transition proofs), producing two `StateMachineUpdated` events. `on_executed` only reads `messages[0]`'s signer, so the reward for *both* state-machine updates — the one legitimately relayed for `A` and the one whose proof/relaying work was actually done by RelayerB for `B` — is paid to the attacker.

This is the same bug class as the OpenClaw advisory: a batch of distinct sender-authorized items is dispatched/settled using only one (the first/attacker-controlled) sender's authorization context, letting privileges/rewards belonging to other legitimate senders bleed into that context.

### Impact Explanation
This directly causes theft of relayer reward funds from the protocol treasury: `Self::process_message` performs a real `T::Currency::transfer` from `T::TreasuryAccount` plus a reputation-token `mint_into` to the attacker's account for state-machine updates it did not itself deliver: [5](#0-4) 

Every legitimate relayer's consensus-update reward in a runtime using `pallet-consensus-incentives` as its `FeeHandler` can be siphoned this way, and because rewards are also gated by a per-state-machine "highest height since last watermark" model (`LastRewardedHeight`), once the attacker's batch lands the watermark advances and the legitimate relayer who actually did the work receives nothing when they submit the same (now redundant) update — this is a direct, unauthorized diversion of funds, satisfying "concrete theft ... of funds."

### Likelihood Explanation
`handle_unsigned` is deliberately permissionless/unsigned and free (no fee is charged, `Pays::No`), and is specifically designed to accept arbitrary batches of messages from anyone with valid proofs. Consensus proofs and relayer signatures broadcast to the transaction pool or gossiped between relayers are public data with no submitter-binding, so re-including someone else's valid, already-signed consensus message inside one's own batch requires no special access — only network visibility of the pending message, which any node/mempool observer or a colluding relayer has. The main variable affecting exploitability is timing (front-running before the original submitter's extrinsic is included), which is a routine MEV-style capability in this ecosystem given the docs' own acknowledgment of a "race to deliver" model for relayers.

### Recommendation
`on_executed` should attribute each `StateMachineUpdated` event to the relayer of the specific `Message::Consensus` entry that produced it, not to `messages[0]` applied to the whole batch. Concretely, iterate `messages` alongside `message_results`/`events`, pair each `Message::Consensus` with the `StateMachineUpdated` event(s) it actually generated (e.g. by matching on the consensus/state-machine id the message targets, or by threading provenance through `MessageResult` rather than a flattened `events` list), and verify/derive the relayer signature per matched message before crediting it. This mirrors how `pallet-messaging-incentives::on_executed` already does it correctly per-message via `relayer_for(&mw.message)`: [6](#0-5) 

### Proof of Concept
1. RelayerA constructs and signs a valid `Message::Consensus` update for state machine `X` (signature over `keccak256(proof_X)` recoverable to `AccountA`).
2. RelayerB independently constructs and signs a valid `Message::Consensus` update for state machine `Y`, and broadcasts it as an unsigned `handle_unsigned([Message::Consensus(Y)])` extrinsic (visible in the transaction pool before inclusion).
3. RelayerA copies RelayerB's `Message::Consensus(Y)` payload verbatim (proof + signature bytes are just data) and submits `handle_unsigned([Message::Consensus(X, signed by A), Message::Consensus(Y, signed by B)])`, front-running RelayerB's own transaction.
4. `Pallet::execute` processes both messages successfully (both proofs are valid), producing `StateMachineUpdated{X}` and `StateMachineUpdated{Y}` events, passed together to `on_executed`.
5. `on_executed` reads only `messages[0]` (`X`, signed by A), recovers `AccountA`, and pays `AccountA` the reward for **both** `X`'s and `Y`'s state-machine updates via `process_message`, transferring treasury funds and minting reputation tokens to `AccountA` for work `AccountB` performed.
6. When RelayerB's original transaction for `Y` is later included (or rejected as redundant), `LastRewardedHeight` for `Y` has already advanced, so RelayerB receives no reward for the update they actually authored and relayed.

### Citations

**File:** modules/pallets/ismp/src/impls.rs (L37-87)
```rust
impl<T: Config> Pallet<T> {
	/// Execute the provided ISMP datagrams, this will short circuit if any messages are invalid.
	/// This also charges fee on valid message delivery
	pub fn execute(messages: Vec<Message>) -> Result<Vec<events::Event>, Error<T>> {
		let host = Pallet::<T>::default();

		let message_results = messages
			.iter()
			.map(|msg| handle_incoming_message(&host, msg.clone()))
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;

		let messages_with_weights = message_results
			.iter()
			.zip(messages)
			.map(|(result, message)| MessageWithWeight { message, weight: result.weight() })
			.collect::<Vec<_>>();

		let events = message_results
			.into_iter()
			// check that requests will be successfully dispatched
			// so we can not be spammed with failing txs
			.map(|result| match result {
				MessageResult::Request { events, .. } |
				MessageResult::Response { events, .. } |
				MessageResult::Timeout { events, .. } => events,
				MessageResult::ConsensusMessage(events) => events.into_iter().map(Ok).collect(),
				MessageResult::FrozenClient(_) => vec![],
			})
			.flatten()
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;

		T::FeeHandler::on_executed(messages_with_weights, events.clone())
			.map_err(|_| Error::<T>::ErrorChargingFee)?;

		for event in events.clone() {
			// deposit any relevant events
			Pallet::<T>::deposit_event(event.into());
		}

		Ok(events)
	}
```

**File:** modules/pallets/ismp/src/lib.rs (L358-382)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Execute the provided batch of ISMP messages, this will short-circuit and revert if any
		/// of the provided messages are invalid. This is an unsigned extrinsic that permits anyone
		/// execute ISMP messages for free, provided they have valid proofs and the messages have
		/// not been previously processed.
		///
		/// The dispatch origin for this call must be an unsigned one.
		///
		/// - `messages`: the messages to handle or process.
		///
		/// Emits different message events based on the Message received if successful.
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L41-75)
```rust
	fn process_message(
		state_machine_height: StateMachineHeight,
		state_machine_id: StateMachineId,
		relayer_account: T::AccountId,
	) -> Result<(), Error<T>> {
		if let Some(block_cost) = StateMachinesCostPerBlock::<T>::get(state_machine_id) {
			let reward = Self::calculate_reward(&state_machine_id, block_cost)?;

			if reward.is_zero() {
				return Ok(());
			}

			T::Currency::transfer(
				&T::TreasuryAccount::get().into_account_truncating(),
				&relayer_account,
				reward,
				Preservation::Expendable,
			)
			.map_err(|_| Error::<T>::RewardTransferFailed)?;

			Self::deposit_event(Event::<T>::RelayerRewarded {
				relayer: relayer_account.clone(),
				amount: reward,
				state_machine_height,
			});

			T::ReputationAsset::mint_into(&relayer_account, reward.saturated_into())
				.map_err(|_| Error::<T>::ReputationMintFailed)?;

			LastRewardedHeight::<T>::mutate(state_machine_id, |watermark| {
				*watermark = Some(watermark.unwrap_or_default().max(state_machine_height.height));
			});
		}
		Ok(())
	}
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L108-122)
```rust
	fn on_executed(
		messages: Vec<MessageWithWeight>,
		events: Vec<IsmpEvent>,
	) -> DispatchResultWithPostInfo {
		let maybe_relayer_account = messages.get(0).and_then(|first_message| {
			if let Message::Consensus(consensus_msg) = &first_message.message {
				let data = sp_io::hashing::keccak_256(&consensus_msg.consensus_proof);
				Signature::decode(&mut &consensus_msg.signer[..])
					.ok()
					.and_then(|sig| sig.verify_and_get_sr25519_pubkey(&data, None).ok())
					.map(|pub_key| pub_key.into())
			} else {
				None::<[u8; 32]>
			}
		});
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L124-157)
```rust
		if let Some(relayer_account) = maybe_relayer_account {
			// When a batch contains multiple `StateMachineUpdated` events for the
			// same `state_machine_id` (sequential consensus updates for the same
			// chain), `calculate_reward` reads the same persisted
			// `(latest_commitment_height, previous_commitment_height)` pair on
			// every iteration and pays the same block-span reward N times.
			// Collapse the per-state-machine event stream to the single highest
			// `latest_height` so each state machine receives one reward per
			// batch, sized by the actual span of its commitment advance.
			let mut highest_per_state_machine: BTreeMap<StateMachineId, u64> = BTreeMap::new();
			for event in events {
				if let IsmpEvent::StateMachineUpdated(update) = event {
					highest_per_state_machine
						.entry(update.state_machine_id)
						.and_modify(|h| {
							if update.latest_height > *h {
								*h = update.latest_height;
							}
						})
						.or_insert(update.latest_height);
				}
			}

			for (state_machine_id, latest_height) in highest_per_state_machine {
				let state_machine_height =
					StateMachineHeight { id: state_machine_id.clone(), height: latest_height };

				let _ = Self::process_message(
					state_machine_height,
					state_machine_id,
					relayer_account.clone().into(),
				);
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
