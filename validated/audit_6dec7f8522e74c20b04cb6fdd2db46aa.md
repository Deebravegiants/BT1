### Title
`pallet-consensus-incentives` attributes rewards for every `StateMachineUpdated` event in a batch to the signer of only the first message - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`FeeHandler::on_executed` in `pallet-consensus-incentives` recovers the relayer account **only from `messages.get(0)`**, then pays out the reward for **every** `StateMachineUpdated` event found anywhere in the whole executed batch to that single recovered account. Because `handle_unsigned` is a permissionless, unsigned extrinsic that accepts an arbitrary `Vec<Message>`, an unprivileged submitter can prepend a cheaply-obtained, self-signed `ConsensusMessage` and append other relayers' legitimate consensus proofs (which are public wire data, not secret), collecting the reward for state advances they did not actually relay.

### Finding Description
`FeeHandler::on_executed` is invoked once per `handle_unsigned`/`execute` call with the full list of processed messages and the full list of emitted events: [1](#0-0) 

`pallet-consensus-incentives`'s implementation only inspects the head of the batch to identify who should be paid: [2](#0-1) 

It then walks **all** events in the batch — not just events produced by that first message — collapses them per `state_machine_id` to the highest `latest_height`, and pays the recovered account for each one: [3](#0-2) 

The `signer` field embedded in every other `Message::Consensus` entry in the batch (entries at index ≥ 1) is never read or verified for reward-attribution purposes; only its cryptographic proof is checked by the ISMP consensus handler for correctness of the state transition, independent of who "owns" the update. The batch is dispatched through the permissionless `handle_unsigned` call: [4](#0-3) 

This is structurally the same bug class as the referenced AshGraphql CVE: an authorization/attribution decision that should be scoped per-item (per relayer, analogous to per-tenant) is instead computed once from the "head" of a collection and then applied in memory across every other item in that collection, without re-checking the correct scope for each one.

### Impact Explanation
Any account can construct a batch `[my_own_signed_consensus_message, someone_else's_valid_consensus_message, ...]` and submit it via `handle_unsigned`. Because consensus proofs and their carrying `ConsensusMessage`s are broadcast/public data (visible in the mempool or already-included blocks), an attacker does not need any private key belonging to the legitimate relayer to replay their message bytes verbatim inside a new batch — only their own key is needed to sign the head message. If the head message is accepted (even a proof that produces no new `StateMachineUpdated` event, e.g., an already-applied/no-op update, provided the consensus client accepts it without erroring), the whole batch succeeds and `on_executed` credits the attacker with the `$BRIDGE` reward and reputation mint for every state-machine advance in the batch, including ones actually produced by another relayer's proof. This is a direct theft of relayer rewards/funds from the treasury (`T::TreasuryAccount`) and an unfair transfer of reputation-asset minting (`T::ReputationAsset::mint_into`), which also feeds into collator-selection weighting per the relayer docs. It can also be used to grief honest relayers by front-running their consensus submissions in this batched form so the attacker's own throwaway message becomes "first."

### Likelihood Explanation
`handle_unsigned` is explicitly permissionless and unsigned — "anyone execute ISMP messages for free, provided they have valid proofs and the messages have not been previously processed" — so no privileged role or admin/governance action is required. The only requirement is possession of a valid consensus proof for the head slot (attacker's own, potentially a cheap/no-op resubmission) plus a second, already-public consensus message from someone else that is genuinely new. Both requirements are readily satisfiable by any network participant capable of running a relayer/observer node, making this Medium-to-High likelihood for an economically motivated actor.

### Recommendation
`on_executed` should attribute each `StateMachineUpdated` reward to the signer of the specific `Message::Consensus` entry that produced it, not to `messages.get(0)`. Concretely: pair each event with the message index/consensus message that generated it (or re-derive/verify a signer per `StateMachineId` from the corresponding message in `messages`, iterating the whole vector rather than only index 0), and reject/ignore events whose originating message cannot be matched to a validly-signed `ConsensusMessage` for that same `state_machine_id`.

### Proof of Concept
1. Attacker observes (via mempool or a recent block) a legitimate `Message::Consensus` `M_B` for state machine `B`, signed by relayer `R_B`, carrying a valid proof that will emit `StateMachineUpdated { state_machine_id: B, latest_height: h }`.
2. Attacker crafts their own `Message::Consensus` `M_A` for a state machine `A` they control/observe, signing it with their own key `K_attacker`, using either a fresh minor update or a replay of an already-applied proof that the consensus client accepts idempotently (no error, possibly no event).
3. Attacker submits `Ismp::handle_unsigned(messages = [M_A, M_B])` as an unsigned extrinsic.
4. `Self::execute` processes both messages; assuming both proofs verify, the batch succeeds and emits `StateMachineUpdated` for `A` (maybe) and for `B` (from `M_B`).
5. `pallet-consensus-incentives::on_executed` is invoked with `messages = [M_A, M_B]`, `events = [.., StateMachineUpdated(A,..), StateMachineUpdated(B,..)]`. It reads `messages[0] == M_A`, recovers `K_attacker`.
6. Reward calculation loops over **all** events, and pays the attacker's account for the `state_machine_id = B` advance as well, even though `R_B` (not the attacker) supplied the actual proof for `B`. [5](#0-4)

### Citations

**File:** modules/pallets/ismp/src/fee_handler.rs (L68-109)
```rust
pub trait FeeHandler {
	/// Process a batch of successfully executed messages and calculate appropriate fees.
	///
	/// This method is invoked once a batch of messages have been successfully processed.
	/// It is the responsibility of implementers to calculate and return the appropriate
	/// `PostDispatchInfo` for fee calculation and settlement based on the messages processed.
	///
	/// ## Parameters
	///
	/// * `messages` - A vector of ISMP protocol messages that have been processed. This includes
	///   various message types such as requests, responses, timeouts, and consensus messages.
	///
	/// ## Returns
	///
	/// Returns a `DispatchResultWithPostInfo` which includes:
	///
	/// * `actual_weight` - The computational weight consumed by processing the messages
	/// * `pays_fee` - Whether the operation should incur fees or not
	///
	/// ## Design Flexibility
	///
	/// This method is deliberately designed to provide flexibility and support a wide range of fee
	/// collection strategies across different blockchain ecosystems. It can accommodate various
	/// economic models including:
	///
	/// * Traditional fee payments where users pay for message processing
	/// * "Negative fees" or incentive structures where relayers receive rewards
	/// * Hybrid models with different fee structures for different message types
	/// * Context-aware pricing based on network conditions or message priority
	///
	/// ## Implementation Considerations
	///
	/// Implementers should consider:
	///
	/// * The computational cost of processing different message types
	/// * Economic incentives for relayers and validators
	/// * Prevention of spam and denial-of-service attacks
	/// * Fairness across different types of network participants
	fn on_executed(
		messages: Vec<MessageWithWeight>,
		events: Vec<Event>,
	) -> DispatchResultWithPostInfo;
```

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
