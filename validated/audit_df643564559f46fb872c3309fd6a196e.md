### Title
Consensus-incentive rewards are attributed to `messages[0]`'s self-declared signer for the *entire* batch, letting an attacker front-run other relayers' consensus proofs and steal their rewards - ([File: modules/pallets/consensus-incentives/src/impls.rs])

### Summary
`pallet-consensus-incentives::on_executed` decodes the relayer/payee only from the **first** message in a `handle_unsigned` batch, then pays that single account for *every* `StateMachineUpdated` event produced anywhere in the batch — including state-machine advances that were actually delivered by a completely different message (and different relayer) later in the same batch. Because `handle_unsigned` is a permissionless, unsigned extrinsic that accepts an arbitrary `Vec<Message>`, and because the `signer` field on a `ConsensusMessage` is a self-declared payee (not something proof verification checks against consensus authenticity), an attacker can prepend a cheap/throwaway valid consensus message of their own in front of another relayer's already-broadcast consensus message, and collect that relayer's reward for delivering state machine B's update — exactly analogous to "Alice" claiming Bribe rewards for an epoch she didn't vote in.

### Finding Description
`FeeHandler::on_executed` is invoked after `pallet_ismp::handle_unsigned` executes a batch of messages: [1](#0-0) 

The relayer identity is derived **only** from `messages.get(0)`: [2](#0-1) 

The batch's `events` (produced by executing *all* messages) are then collapsed per `state_machine_id` and every resulting reward is paid to that single `relayer_account`, regardless of which message in the batch actually produced the corresponding `StateMachineUpdated` event: [3](#0-2) 

`handle_unsigned` accepts an arbitrary, attacker-controlled `Vec<Message>` and is explicitly designed to let "anyone execute ISMP messages for free": [4](#0-3) 

Because the `signer` on `ConsensusMessage` is merely a self-declared reward-payee (verified only as *some* valid signature, not tied to who actually produced/relayed the underlying consensus proof), and because consensus proofs themselves are derived from public chain data (BEEFY/GRANDPA/etc. signatures, not a private submission key), any actor can:
1. Observe another relayer's pending/valid `Message::Consensus` for state machine `B` (e.g. from the public mempool, or simply reconstruct the same proof independently from public source-chain data).
2. Copy that message unmodified into their own batch as `messages[1]`.
3. Prepend their own cheap/self-authored valid consensus message for state machine `A` as `messages[0]`, with `signer` set to their own account.
4. Submit `handle_unsigned([msg_A_attacker, msg_B_victim])`.

`Self::execute` processes both messages and returns `StateMachineUpdated` events for both `A` and `B`. `on_executed` only reads `messages[0]`'s signer (the attacker), then pays the attacker for **both** `A`'s and `B`'s block-span rewards — including the reward that rightfully belongs to whoever delivered `B`.

This is the same root cause as the Alchemix `Bribe.getRewardForOwner` bug: a reward-accounting path grants payout based on a stale/misattributed reference (the checkpoint balance in Alchemix; `messages[0]`'s signer here) instead of verifying that the specific beneficiary actually did the work (voted in that epoch; delivered that specific state machine update).

### Impact Explanation
This allows systematic theft of relayer incentive rewards from the `TreasuryAccount`, and denial of rightful earnings to the relayers who actually source and deliver state machine updates (analogous to "users that voted cannot receive their share"). Since `calculate_reward` pays `blocks_since_last_reward * cost_per_block` (potentially large spans after downtime), and the `LastRewardedHeight` watermark advances regardless of who is credited, repeated exploitation drains the treasury to an attacker doing no real relaying work for the state machines they piggyback on, while legitimate relayers who invest in generating/submitting expensive proofs are never paid — a direct case of misdirected fund transfer / relayer-reward-accounting insolvency, matching the "Protocol insolvency" / "relayer fee and reward accounting" impact class in scope.

### Likelihood Explanation
High. `handle_unsigned` is intentionally permissionless and unsigned (spam-protected only via `validate_unsigned`/txpool tags), so any party can submit arbitrary message batches. Front-running or simply appending an observed valid consensus message from another relayer costs nothing beyond the attacker's own cheap message, and the exploit requires no cryptographic breaks — only reordering messages within a single batch.

### Recommendation
Attribute rewards per message/per `StateMachineUpdated` event to the signer of the specific `Message::Consensus` that produced that event, not to `messages[0]` for the whole batch. Concretely, `on_executed` should walk `messages` alongside `events`, pairing each consensus message's decoded signer with the state-machine id(s) it actually advanced (e.g. by tracking, during `execute`, which message produced which `StateMachineUpdated` event), and reward only that pairing — mirroring how `pallet-relayer`'s `OutboundConsensusRotationsClaimed`/`OutboundRequestsClaimed` attribute rewards strictly per verified delivery rather than per batch position.

### Proof of Concept
Conceptual reproduction (pallet-level, using the existing testsuite harness style in `modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs`):
1. Configure `StateMachinesCostPerBlock` for two chains `A` (cheap/no-op) and `B` (high value), and fund `TreasuryAccount`.
2. Relayer V builds a valid `Message::Consensus` for chain `B` that advances its `latest_commitment_height` by many blocks, with `signer` = V's key.
3. Attacker M builds a trivial valid `Message::Consensus` for chain `A` (even a no-op/minimal advance) with `signer` = M's key.
4. Attacker M submits `pallet_ismp::handle_unsigned([msg_A_M, msg_B_V])` (copying V's untouched message).
5. Observe: `on_executed` decodes `relayer_account = M` from `messages[0]`, then iterates the collapsed `highest_per_state_machine` map containing both `A` and `B`, paying **M** for both `A`'s and `B`'s reward — verify via `RelayerRewarded` events and `T::Currency` balance changes that V received nothing for state machine `B` despite having authored/sourced that proof.

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L108-157)
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
