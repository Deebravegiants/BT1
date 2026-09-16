### Title
Stale `LastRewardedHeight` watermark not reset on `remove_incentives` causes retroactive over-payment of relayer rewards when incentives are re-enabled - (File: modules/pallets/consensus-incentives/src/lib.rs, modules/pallets/consensus-incentives/src/impls.rs)

### Summary
`pallet-consensus-incentives` rewards the relayer that delivers a consensus proof based on the number of blocks advanced since a per-state-machine watermark, `LastRewardedHeight`. When governance calls `remove_incentives` to pause rewards for a state machine, only `StateMachinesCostPerBlock` is cleared; `LastRewardedHeight` is left untouched. Because the watermark is only advanced inside the reward-paying branch, it freezes at whatever height it had when incentives were disabled. Once `update_cost_per_block` re-enables rewards, the very next relayer to submit a valid consensus proof is paid for the *entire* span since the frozen watermark — including all the blocks that advanced while incentives were intentionally disabled — an unintended retroactive payout drawn from the treasury.

### Finding Description
`remove_incentives` only removes the cost entry: [1](#0-0) 

`LastRewardedHeight` is a monotonically-advancing watermark that is only mutated when a reward is actually paid, i.e. only inside the `if let Some(block_cost) = ...` branch of `process_message`: [2](#0-1) 

While `StateMachinesCostPerBlock` is absent (post-removal), `process_message` short-circuits before touching `LastRewardedHeight`, so the watermark stops advancing even though the underlying state machine height (via `IsmpHost::latest_commitment_height`) keeps moving forward as consensus messages continue to be relayed and processed by `pallet-ismp` for that chain — dispatch of new consensus messages is not gated by whether incentives are configured. When incentives are re-enabled with `update_cost_per_block`, `calculate_reward` computes: [3](#0-2) 

`baseline` resolves to the stale, frozen `LastRewardedHeight`, so `blocks = latest_height - baseline` now spans the entire disabled period plus the enabled period. The very next relayer to have their consensus message processed collects `blocks_as_balance * cost_per_block` for that full span — a reward the treasury never intended to pay, since governance explicitly removed the cost during that window. This mirrors the reported SymmStaking bug class exactly: an accounting checkpoint (`userRewardPerTokenPaid` / here `LastRewardedHeight`) is not reset when a reward source is disabled and re-enabled, so whichever party benefits from the checkpoint gap receives rewards for a period it should not have accrued for.

### Impact Explanation
This results in an unbacked/unintended payout of `T::Currency` from the treasury account and unbacked minting of `T::ReputationAsset` to whichever relayer happens to deliver the next consensus message after re-enabling, proportional to however long the state machine's incentives were disabled and how far its commitment height advanced in the interim. Since consensus updates for a given `StateMachineId` are permissionlessly submittable/relayable (any relayer can be the one whose message is included, as this is the standard, unprivileged consensus-relaying dispatch path feeding `FeeHandler::on_executed`), an opportunistic relayer can capture an outsized, unintended reward simply by being first to relay after re-enable. This drains treasury funds beyond what governance authorized and can be repeated for any state machine that is ever paused and resumed.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment that uses `remove_incentives` operationally (e.g., temporarily pausing rewards for a chain during maintenance, cost re-pricing, or an incident) and later re-enables them via `update_cost_per_block` — a normal governance workflow. No special conditions are required beyond the state machine continuing to receive consensus updates during the disabled window, which is expected default behavior since message relaying/consensus processing is not coupled to the incentives configuration.

### Recommendation
When `remove_incentives` clears `StateMachinesCostPerBlock` for a `state_machine_id`, also reset (e.g., set to the current `latest_commitment_height`, or remove) the corresponding `LastRewardedHeight` entry so that re-enabling incentives via `update_cost_per_block` establishes a fresh baseline at that point rather than resuming from the stale pre-removal watermark.

### Proof of Concept
1. `IncentivesOrigin` calls `update_cost_per_block(sm_id, cost)`, enabling rewards for state machine `sm_id`.
2. A relayer submits a consensus proof advancing `sm_id` to height `H1`; `process_message` pays the relayer and sets `LastRewardedHeight[sm_id] = H1`. [4](#0-3) 
3. `IncentivesOrigin` calls `remove_incentives(sm_id)`, clearing `StateMachinesCostPerBlock[sm_id]` (intending to stop rewards) but leaving `LastRewardedHeight[sm_id] = H1`.
4. Consensus messages for `sm_id` continue to be relayed/processed normally (unrelated to the incentives pallet), advancing the chain's commitment height to `H2` (`H2 >> H1`) with no reward paid (since `StateMachinesCostPerBlock::get` is `None`, `LastRewardedHeight` is not updated).
5. `IncentivesOrigin` calls `update_cost_per_block(sm_id, cost)` again, re-enabling rewards.
6. The next relayer whose consensus message is processed advances `sm_id` to `H3`; `calculate_reward` computes `baseline = LastRewardedHeight::get() = H1`, so `blocks = H3 - H1`, paying the relayer for the entire disabled span (`H1` to `H2`) plus the newly enabled span — an unintended, outsized transfer from the treasury and unbacked mint of `ReputationAsset`. [5](#0-4)

### Citations

**File:** modules/pallets/consensus-incentives/src/lib.rs (L152-166)
```rust
		/// Update cost per block for a state machine
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::update_cost_per_block())]
		pub fn remove_incentives(
			origin: OriginFor<T>,
			state_machine_id: StateMachineId,
		) -> DispatchResult {
			T::IncentivesOrigin::ensure_origin(origin)?;

			StateMachinesCostPerBlock::<T>::remove(state_machine_id.clone());

			Self::deposit_event(Event::<T>::StateMachineCostPerBlockRemoved { state_machine_id });

			Ok(())
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
