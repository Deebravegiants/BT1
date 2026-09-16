### Title
Unbacked relayer reward mint from unbounded first-claim height span - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`Pallet::calculate_reward` in `pallet-consensus-incentives` computes a relayer's reward as `(latest_height - baseline) * block_cost`, where `baseline` falls back to `previous_commitment_height` (itself defaulted to `0` via `unwrap_or_default()`) whenever `LastRewardedHeight` has never been set for a state machine. [1](#0-0)  This mirrors the reported bug class exactly: an unset/empty checkpoint value (there, `_totalCheckpoints`; here, `LastRewardedHeight`/`previous_commitment_height`) silently resolves to zero and is fed directly into a payout/quorum calculation, producing a result that is unbacked by any real accrual.

### Finding Description
`process_message` looks up `StateMachinesCostPerBlock` and calls `calculate_reward`, which computes `blocks = latest_height.saturating_sub(baseline)` and then `reward = blocks_as_balance.saturating_mul(block_cost)`. [2](#0-1)  `baseline` is derived as `LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height)`, and `previous_height` itself is `host.previous_commitment_height(...).unwrap_or_default()` — i.e., it silently becomes `0` any time the host cannot report a genuinely-previous committed height for that state machine (freshly-onboarded state machine, host storage gap, or any other case where `previous_commitment_height` returns `None`). [3](#0-2) 

When both `LastRewardedHeight` is unset (first-ever reward for that chain) and `previous_commitment_height` returns `None`/default, `baseline` collapses to `0`. The reward then becomes `latest_height * block_cost` instead of `(latest_height - previous_height) * block_cost` — i.e., the relayer is paid for the entire historical height range of the state machine as if they had single-handedly delivered every block from genesis, rather than just the span actually advanced by their submitted consensus message. This is the same root-cause shape as the reported bug: a checkpoint that should reflect prior state is empty/zero, so a downstream financial calculation (quorum in the original report, reward payout here) is computed against a bogus zero baseline, inflating (rather than zeroing) the result but coming from the identical logic flaw — trusting a default/empty value for a monotonic checkpoint in a security-critical arithmetic calculation.

The payout path is directly triggered by `FeeHandler::on_executed`, invoked whenever a relayer submits a `Message::Consensus` message that produces `StateMachineUpdated` events; the relayer identity is recovered from the message's own signature, meaning any unprivileged relayer who submits the first-ever accepted consensus update for a given `state_machine_id` (or one after `previous_commitment_height` is otherwise unavailable) triggers the inflated payout, then unconditionally receives a real `Currency::transfer` from the treasury plus a matching reputation-asset mint. [4](#0-3) [5](#0-4) 

### Impact Explanation
`T::Currency::transfer` moves real treasury balance to the relayer account, and `T::ReputationAsset::mint_into` mints reputation tokens, both sized by the erroneously large `blocks` span. [6](#0-5)  For a state machine whose `latest_height` is large (e.g., an EVM chain already at height in the millions) being onboarded or hitting this zero-baseline condition, the reward computed as `latest_height * block_cost` can be a massive, economically unjustified drain on the treasury — a direct theft/unbacked-mint of funds triggered by a normal relayer action, not by any admin/governance misconfiguration.

### Likelihood Explanation
This path is reached by the ordinary, permissionless act of relaying a consensus update — no privileged role is required, and the FeeHandler is invoked automatically as part of message execution (`on_executed`). [7](#0-6)  The vulnerable state (baseline == 0) naturally occurs the first time a state machine's reward path fires, or any time `previous_commitment_height` returns `None`, which is a routine, not adversarial-only, condition (e.g., newly configured state machine, or genesis-adjacent onboarding).

### Recommendation
Do not default the baseline to `0`/`previous_height` when no prior reward watermark and no genuinely-prior commitment exist. Instead, when `LastRewardedHeight` is unset, initialize the baseline to `latest_height` on first observation (i.e., record the watermark without paying for the unobserved historical span), or require an explicit governance-set starting height per state machine before any reward accrual begins. This prevents any single relayer message from being credited for state-machine height progress that occurred before the state machine's incentive tracking began — analogous to fixing `getPastTotalSupply` to reflect actual minted supply instead of an empty checkpoint.

### Proof of Concept
1. Configure `StateMachinesCostPerBlock` for a new `state_machine_id` whose underlying light client is already synced to a high `latest_height` (e.g., height 5,000,000), with `LastRewardedHeight` unset and `previous_commitment_height` returning `None`/default for that id. [8](#0-7) 
2. As any unprivileged relayer, submit a `Message::Consensus` message that produces a `StateMachineUpdated` event for that `state_machine_id`. [9](#0-8) 
3. `on_executed` calls `process_message` → `calculate_reward`, computing `blocks = latest_height - 0 = 5,000,000` and `reward = 5,000,000 * block_cost`. [10](#0-9) 
4. The pallet transfers this inflated `reward` from the treasury to the relayer and mints matching reputation assets, then sets `LastRewardedHeight` to `latest_height`, permanently draining the treasury for a single relay action. [11](#0-10) 

Note: I was unable to inspect the exact implementation of `previous_commitment_height`/`latest_commitment_height` in `modules/pallets/ismp/src/host.rs` (file read was truncated/unavailable via the index), so the precise conditions under which `previous_commitment_height` returns `None` for a given state machine could not be fully confirmed from source; this should be verified directly in that file before finalizing severity.

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L41-72)
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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L108-156)
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
```
