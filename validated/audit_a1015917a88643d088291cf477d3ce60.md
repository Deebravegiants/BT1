### Title
Stale reward watermark combined with rate updates in `pallet-consensus-incentives` allows relayers to drain the treasury by withholding consensus proofs until `cost_per_block` increases - (File: `modules/pallets/consensus-incentives/src/impls.rs`, `modules/pallets/consensus-incentives/src/lib.rs`)

### Summary
`pallet_consensus_incentives::calculate_reward` pays out `(latest_height - baseline) * block_cost` where `baseline` is the last-rewarded watermark and `block_cost` is whatever `StateMachinesCostPerBlock` currently holds [1](#0-0) . Because the reward span is measured from the persisted watermark but priced at the *current* rate, any governance rate change is retroactively applied to the entire unpaid backlog, exactly like the Masterchef `lumPerSecond`/weight bug: a stale "last updated" pointer combined with a rate change that is applied across the whole stale interval instead of being settled first.

### Finding Description
`update_cost_per_block` immediately overwrites `StateMachinesCostPerBlock` for a state machine with no requirement to first flush/settle the pending reward for blocks already produced under the old rate [2](#0-1) . The `LastRewardedHeight` watermark only advances when `process_message` actually pays a reward [3](#0-2) , so any state machine that has gone a while without a relayer submitting a `ConsensusMessage` accumulates an unpaid `(latest_height - baseline)` span. `calculate_reward` then multiplies that *entire accumulated span* by whatever `block_cost` is in storage at the moment the next `ConsensusMessage` is processed [4](#0-3)  — not the rate(s) that were actually in effect while those blocks were produced.

Since submitting consensus messages is fully permissionless (any relayer can choose when to submit a `ConsensusMessage`, and `on_executed` recovers the relayer's signature to identify who gets paid) [5](#0-4) , a relayer can deliberately withhold consensus proofs for a state machine, wait for governance to raise `StateMachinesCostPerBlock` (a routine parameter update, not a malicious admin action), and then submit a single consensus update that collects the entire withheld backlog priced at the new, higher rate — receiving both an inflated `Currency::transfer` from the treasury and inflated `ReputationAsset` mint [6](#0-5) .

This is the same root cause as the H-3 report: the reward-accrual mechanism assumes the current rate applied since the last settlement point, but nothing forces settlement of the outstanding window at the old rate before the rate changes.

### Impact Explanation
The treasury pallet-consensus-incentives pays from is drained beyond the amount actually earned for the withheld period, because the entire backlog is priced at the post-update rate instead of the rate(s) that applied while those blocks were relayed/finalized. Because relayer submission is unprivileged and timing is entirely within the relayer's control, this is directly exploitable by any permissionless relayer without needing any malicious governance action — governance merely has to perform an ordinary, legitimate `update_cost_per_block` call (e.g., raising the reward to reflect higher infra costs) for the exploit window to open. This constitutes unbacked/over-minted reward payout and direct theft of treasury funds, meeting the High/Medium bar for concrete fund loss.

### Likelihood Explanation
Likelihood is moderate to high: any relayer can trivially withhold submission of a `ConsensusMessage` for a state machine they serve (submission is optional/permissionless), and cost-per-block updates are a normal, expected governance operation (not a rare or adversarial event) meant to keep pace with changing infrastructure costs. No special privileges or race conditions are required beyond simple timing.

### Recommendation
Before or as part of `update_cost_per_block` (and `remove_incentives`), settle any outstanding reward for each affected state machine at the *old* rate and advance `LastRewardedHeight` to the current `latest_commitment_height`, mirroring the "call `updateAll` before changing weights" fix applied to the Masterchef issue. Alternatively, split the accrual so that reward calculation tracks the rate that was in effect during each sub-interval (e.g., store `(height, rate)` checkpoints) rather than applying a single current rate across a potentially stale span.

### Proof of Concept
1. Governance sets `cost_per_block = X` for `state_machine_id = SM` via `update_cost_per_block` [7](#0-6) .
2. `SM` advances from height `H0` to `H1` on-chain, but no relayer submits a `ConsensusMessage` for it (relaying is optional), so `LastRewardedHeight[SM]` stays at `H0`.
3. Governance later raises `cost_per_block` to `Y > X` for legitimate reasons (routine parameter tuning).
4. A relayer who has been withholding proofs for `SM` now submits a single `ConsensusMessage` advancing the recorded latest height to `H1`.
5. `calculate_reward` computes `reward = (H1 - H0) * Y` [8](#0-7) , paying the relayer at the new higher rate `Y` for the entire `H1 - H0` span, even though most of that span occurred while the rate was still `X`. The treasury pays `(H1 - H0) * (Y - X)` more than it should have.

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L46-73)
```rust
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
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L86-99)
```rust
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

**File:** modules/pallets/consensus-incentives/src/lib.rs (L128-150)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Update cost per block for a state machine
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::update_cost_per_block())]
		pub fn update_cost_per_block(
			origin: OriginFor<T>,
			state_machine_id: StateMachineId,
			cost_per_block: <T as pallet_ismp::Config>::Balance,
		) -> DispatchResult {
			T::IncentivesOrigin::ensure_origin(origin)?;

			StateMachinesCostPerBlock::<T>::mutate(state_machine_id.clone(), |maybe_cost| {
				*maybe_cost = Some(cost_per_block);
			});

			Self::deposit_event(Event::<T>::StateMachineCostPerBlockUpdated {
				state_machine_id,
				cost_per_block,
			});

			Ok(())
		}
```
