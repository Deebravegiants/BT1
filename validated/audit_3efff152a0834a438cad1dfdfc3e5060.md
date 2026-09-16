### Title
First consensus update for a newly registered state machine pays a reward for its entire pre-existing height, draining treasury funds and unbacked-minting ReputationAsset - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`pallet-consensus-incentives::calculate_reward` computes a relayer's reward as `(latest_height - baseline) * block_cost`, where `baseline` falls back to `previous_commitment_height` when no `LastRewardedHeight` watermark exists yet. For a state machine that has never been rewarded before, `previous_commitment_height` is itself seeded to `0` the very first time `store_latest_commitment_height` is called for that id. The result is that the *first* consensus update ever recorded for a state machine is rewarded as if the relayer had delivered every block from genesis (height 0) up to whatever height that update reports — not just the actual span of work performed. This mirrors the TempleGold bug class: a per-unit accrual computation that is never given a proper baseline on first use, so the first invocation is credited for the entire un-initialized interval instead of zero.

### Finding Description
`calculate_reward` in `modules/pallets/consensus-incentives/src/impls.rs`: [1](#0-0) 

- `latest_height` comes from `IsmpHost::latest_commitment_height`.
- `previous_height` falls back to `.unwrap_or_default()` (0) if `previous_commitment_height` returns `None`.
- `baseline = LastRewardedHeight::get(id).unwrap_or(previous_height)` — for a brand-new state machine id, `LastRewardedHeight` is `None`, so `baseline` becomes `previous_height`.

The `previous_commitment_height` value is written by `store_latest_commitment_height` in `modules/pallets/ismp/src/host.rs`: [2](#0-1) 

On the very first call for a given `state_machine_id`, `LatestStateMachineHeight::get(id)` is `None`, so `previous_height` (stored into `PreviousStateMachineHeight`) is set to `0`, not to the incoming height. Consequently, `calculate_reward`'s `baseline` is `0` for the first reward computation on that chain, and `blocks = latest_height.saturating_sub(0) = latest_height` — the chain's entire existing height at the moment it is registered/first updated on Hyperbridge, rather than the span of blocks the relayer actually advanced.

`process_message` then unconditionally pays this reward out of the treasury and mints an equal amount of `ReputationAsset`: [3](#0-2) 

`on_executed` (the `FeeHandler` entrypoint) is invoked as part of processing a `Message::Consensus` submitted via the permissionless `pallet_ismp::Pallet::handle_unsigned` extrinsic — any relayer can construct and submit this once a `StateMachinesCostPerBlock` entry exists for the target chain: [4](#0-3) 

### Impact Explanation
- **Unbacked mint:** `T::ReputationAsset::mint_into(&relayer_account, reward)` executes with no supply cap tied to the reward's correctness, so a reward inflated by an un-initialized baseline results in an unbacked mint of ReputationAsset tokens scaled to the entire pre-existing height of the newly onboarded chain.
- **Treasury drain:** `T::Currency::transfer` pays the same inflated `reward` amount from the treasury account to whichever relayer is first to submit a valid consensus proof for a newly configured state machine, up to the treasury's balance. Onboarding any moderately mature chain (hundreds of thousands to millions of blocks) with a non-trivial `block_cost` can produce a reward vastly exceeding the intended per-block-worked incentive, and the relayer who wins this race captures it.
- This is directly triggerable by any permissionless relayer submitting a consensus message the moment governance configures `StateMachinesCostPerBlock` for a state machine that is not brand new (i.e., already at a nonzero height on its own chain) — a routine, expected operational step, not an edge case.

### Likelihood Explanation
High for any chain onboarded to Hyperbridge with non-trivial existing height and a nonzero `block_cost`: the very first `StateMachineUpdated` event for that `state_machine_id` after `update_cost_per_block` is set will trigger this path. No attacker privilege is required beyond being the first (or any) relayer to submit the initial consensus proof, which is the normal, expected relaying flow.

### Recommendation
When a state machine id is seen for the first time (i.e., `previous_commitment_height`/`LastRewardedHeight` are both absent), initialize the reward baseline to the incoming `latest_height` instead of `0`, so the first update yields zero reward and subsequent updates are scoped to genuine incremental spans — analogous to initializing `_lastMintTimestamp` at first use in the TempleGold fix. Concretely, in `store_latest_commitment_height`, seed `PreviousStateMachineHeight` to the new height (not `0`) when no prior entry exists, or equivalently have `calculate_reward` treat a missing `LastRewardedHeight` **and** missing prior commitment as "baseline = latest_height" for that first observation.

### Proof of Concept
1. Governance calls `pallet_consensus_incentives::update_cost_per_block(root, state_machine_id, block_cost)` for a chain that, off-chain, is already at height `H` (e.g. `H = 5_000_000`).
2. A relayer submits the first valid `Message::Consensus` update for `state_machine_id` reporting `latest_height = H`.
3. `pallet_ismp::Pallet::handle_unsigned` processes it; `IsmpHost::store_latest_commitment_height` runs with `LatestStateMachineHeight::get(id) == None`, so `previous_height = 0` is stored into `PreviousStateMachineHeight`.
4. `FeeHandler::on_executed` → `process_message` → `calculate_reward`: `previous_height = host.previous_commitment_height(id) == Some(0)`, `LastRewardedHeight::get(id) == None` so `baseline = 0`; `blocks = H - 0 = H`.
5. `reward = H * block_cost` is transferred from the treasury to the relayer and an equal amount is minted into the relayer's `ReputationAsset` balance — as demonstrated by the existing test `test_incentivize_relayer` (`modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs:87-112`), which shows the reward scaling directly with `latest_height` on the very first update, confirming the baseline-is-zero behavior.

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L53-68)
```rust
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
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L82-99)
```rust
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
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L104-157)
```rust
impl<T: Config> FeeHandler for Pallet<T>
where
	<T as frame_system::Config>::AccountId: From<[u8; 32]>,
{
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

**File:** modules/pallets/ismp/src/host.rs (L229-234)
```rust
	fn store_latest_commitment_height(&self, height: StateMachineHeight) -> Result<(), Error> {
		let previous_height = LatestStateMachineHeight::<T>::get(height.id).unwrap_or_default();
		PreviousStateMachineHeight::<T>::insert(height.id, previous_height);
		LatestStateMachineHeight::<T>::insert(height.id, height.height);
		Ok(())
	}
```
