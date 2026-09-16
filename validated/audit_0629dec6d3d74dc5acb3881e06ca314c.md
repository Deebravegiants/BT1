### Title
Misattribution of `pallet-consensus-incentives` rewards allows theft of treasury `$BRIDGE` funds and reputation by any relayer batching a foreign `ConsensusMessage` - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`pallet-consensus-incentives::Pallet::on_executed` (the `FeeHandler` hook invoked by `pallet-ismp::handle_unsigned`) identifies the relayer to reward by recovering the signer from **only the first message in the batch** (`messages.get(0)`), then pays out rewards for **every** `StateMachineUpdated` event produced by the whole batch, regardless of which `ConsensusMessage` actually produced each event.

### Finding Description
`handle_unsigned` is an unsigned, permissionless extrinsic that accepts an arbitrary `Vec<Message>` batch and, after successful verification/execution, calls `FeeHandler::on_executed(messages, events)` [1](#0-0) . Because it is unsigned/permissionless, anyone can assemble the batch and choose its ordering; the only requirement is that every message in the batch carries a valid proof/signature of its own.

Inside `pallet-consensus-incentives`, the relayer credited for the reward is derived exclusively from `messages[0]`: [2](#0-1) 

But the rewarded events are collected from the **entire** `events` vector passed to the call, spanning every `StateMachineUpdated` produced by any message in the batch, and one reward transfer + reputation mint is issued per state machine advanced: [3](#0-2) [4](#0-3) 

`calculate_reward` pays `(latest_height - baseline) * cost_per_block`, purely a function of the state-machine height span, with no check that `messages[0]`'s signer is the one who produced that particular chain's advance: [5](#0-4) 

A malicious relayer can therefore:
1. Watch the transaction pool / offchain storage for another relayer's legitimate `ConsensusMessage` for chain B (which will advance `latest_commitment_height` for B and mint a real reward).
2. Front-run by submitting their own `handle_unsigned` batch containing their own cheap/no-op `ConsensusMessage` (e.g., a proof for chain A, signed with the attacker's own key) as `messages[0]`, followed by the victim's already-broadcast `ConsensusMessage` for chain B as `messages[1]`.
3. Because `on_executed` only recovers the signer of `messages[0]`, **all** `StateMachineUpdated` rewards in the batch — for chain A **and** chain B — are transferred to the attacker's account, and reputation is minted to the attacker instead of the actual submitter of chain B's proof.

The design intent (per the pallet's own comment) was only to fix double-payment when multiple `StateMachineUpdated` events exist for the *same* state machine in one batch — it collapses to the highest height per state machine — but it never validates that the attributed relayer (`messages[0]`'s signer) is actually responsible for each state machine's event [6](#0-5) .

### Impact Explanation
This is a direct on-chain theft of `TreasuryAccount` funds (`$BRIDGE`) and unearned minting of the non-transferable reputation asset, which in turn feeds into collator selection (per the relayers documentation, reputation is "the primary input to collator selection") [7](#0-6) . An attacker can systematically drain the consensus-incentives treasury by piggybacking off every honest relayer's real proof submissions, and can inflate their own reputation to bias collator selection — a protocol-level, permissionless, single-transaction exploit requiring no privileged role.

### Likelihood Explanation
High. `handle_unsigned` is explicitly permissionless/unsigned and batches are attacker-controlled [1](#0-0) . Consensus proofs for external chains are public data (broadcast to the Hyperbridge tx pool or derivable from source-chain finality), so front-running/bundling a victim's proof behind the attacker's own cheap proof is straightforward and requires only minimal cost (submitting one extra trivial consensus message).

### Recommendation
Attribute each `StateMachineUpdated` reward to the signer of the specific `ConsensusMessage` that produced it, rather than defaulting to `messages[0]`. This requires correlating each event's `state_machine_id` back to the message (or messages) in the batch whose consensus proof actually advanced that specific chain, and recovering/verifying the signer per-message rather than once for the whole batch.

### Proof of Concept
1. Relayer H submits (or has broadcast) a valid `ConsensusMessage` for chain B that will produce `StateMachineUpdated { state_machine_id: B, latest_height: N }` when executed via `handle_unsigned`.
2. Attacker A crafts their own valid (but otherwise irrelevant/cheap) `ConsensusMessage` for chain A signed with A's key.
3. Attacker A submits `handle_unsigned([msg_A_for_chainA, msg_H_for_chainB])` before H's own submission lands (unsigned extrinsics compete on inclusion, not nonce).
4. `pallet_ismp::Pallet::handle_unsigned` processes both messages successfully, producing `events = [StateMachineUpdated(A, ...), StateMachineUpdated(B, N)]`.
5. `pallet_consensus_incentives::Pallet::on_executed` recovers only A's pubkey from `messages[0]` and pays A both the chain-A reward (legitimately) and the chain-B reward that should belong to H — verifiable against the existing test harness pattern in `modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs` (`test_incentivize_relayer`), which can be extended to a 2-message batch with distinct signers to observe the reward misattribution described above. [8](#0-7)

### Citations

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L253-258)
```text
| `handle_unsigned` | Unsigned | Execute the provided batch of ISMP messages for free with valid proofs. This will short-circuit and revert if any of the provided messages are invalid. |
| `fund_message` | Signed | Increase the relayer fee for in-flight requests and responses to incentivize their delivery. Should not be called on a message that has been completed (delivered or timed-out) as those funds will be lost forever. |

## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L77-100)
```rust
	/// Calculate the reward for a message based on the state machine id
	fn calculate_reward(
		state_machine_id: &StateMachineId,
		block_cost: <T as pallet_ismp::Config>::Balance,
	) -> Result<<T as pallet_ismp::Config>::Balance, Error<T>> {
		let host = <T::IsmpHost>::default();
		let latest_height = host
			.latest_commitment_height(state_machine_id.clone())
			.map_err(|_| Error::<T>::CouldNotGetStateMachineHeight)?;
		let previous_height =
			host.previous_commitment_height(state_machine_id.clone()).unwrap_or_default();

		// Use the rewarded watermark as the baseline and fall back to the previous height until
		// the first reward is recorded for this chain. The watermark only moves forward, so a
		// height that is rolled back and later resubmitted is not paid for a second time.
		let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);

		let blocks = latest_height.saturating_sub(baseline);

		let blocks_as_balance: <T as pallet_ismp::Config>::Balance = blocks.saturated_into();
		let reward = blocks_as_balance.saturating_mul(block_cost);

		Ok(reward)
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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L124-163)
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

		// Return with actual weight information
		// We use Pays::No to indicate that someone (the message sender) doesn't pay for this
		// operation, though we're using this mechanism to reward relayers rather than charge fees
		Ok(PostDispatchInfo { actual_weight: None, pays_fee: Pays::No })
	}
```

**File:** docs/content/developers/explore/relayers.mdx (L73-79)
```text
### Rewards

Consensus relayers are paid in `$BRIDGE` on every accepted update,
plus a **non-transferable reputation asset** at a 1:1 ratio.
Reputation is the primary input to [collator selection](/developers/network/collator):
the more proofs you submit, the better your chances of being selected
to author Hyperbridge blocks.
```

**File:** modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs (L87-112)
```rust
#[test]
fn test_incentivize_relayer() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		let host = Ismp::default();
		let state_machine_id = setup_state_machine();

		pallet_consensus_incentives::Pallet::<Test>::update_cost_per_block(
			RuntimeOrigin::root(),
			state_machine_id,
			100,
		)
		.unwrap();

		let (consensus_message, relayer_account) = setup_host_and_message(&host);

		pallet_ismp::Pallet::<Test>::handle_unsigned(
			RuntimeOrigin::none(),
			vec![consensus_message],
		)
		.unwrap();

		assert_eq!(Balances::balance(&relayer_account), UNIT + 4200);
		assert_eq!(Assets::balance(ReputationAssetId::get(), &relayer_account), 4200);
	})
}
```
