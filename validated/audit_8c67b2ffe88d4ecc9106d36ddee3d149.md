### Title
Consensus relayer rewards computed with the current `cost_per_block` rate applied retroactively to the entire unpaid block span - ([File: modules/pallets/consensus-incentives/src/impls.rs])

### Summary
`pallet-consensus-incentives` rewards relayers for delivering consensus updates by multiplying the number of new blocks a consensus message advances (`latest_height - baseline`) by whatever `cost_per_block` rate is currently stored for that state machine, exactly the reward-calculation pattern flagged in the external report as "using the current rate regardless of any changes... between the start and now." If `update_cost_per_block` changes the rate while blocks in the span were already produced under the old rate, the entire span — old and new blocks alike — is paid at the single rate in effect at the moment the relayer's message is processed, rather than being split proportionally per the rate that applied to each sub-range.

### Finding Description
`calculate_reward` computes the reward as: [1](#0-0) 

`baseline` is the last-rewarded watermark and `latest_height` is the newest committed height for the state machine; `blocks = latest_height - baseline` is multiplied by a single `block_cost` value fetched from `StateMachinesCostPerBlock` at call time: [2](#0-1) 

`StateMachinesCostPerBlock` is a single current-value map with no history and no index/accumulator tracking how the rate evolved over time: [3](#0-2) 

`update_cost_per_block` simply overwrites the stored rate in place with no snapshotting of the previous rate or the block height at which it changed: [4](#0-3) 

Because relayers control the timing of when they submit a `ConsensusMessage` (an unprivileged, permissionless action), any relayer who delays submitting a proof that advances the chain across a governance rate change will have the *entire* accumulated unpaid span (potentially spanning long periods under a lower/old rate) paid out entirely at whichever rate is active the instant they submit. This is the same root cause the external report describes for `DIAWhitelistedStaking.getRewardForStakingStore`: reward accrued over a period is computed using only the "current" rate rather than the rate(s) actually in effect during each sub-interval of that period.

### Impact Explanation
If governance raises `cost_per_block` (e.g., in response to a new, more expensive/urgent state machine), any relayer holding an unsubmitted but already-observed consensus advance can submit it right after the increase and collect the higher rate for blocks that accrued entirely under the old, lower rate — over-draining the `TreasuryAccount` beyond what governance intended to allocate for that historical span. Because rewards come straight out of the treasury via `T::Currency::transfer`, this is a direct, unbounded (bounded only by span size × new rate) loss of treasury funds: [5](#0-4) 
Conversely, if the rate is lowered, relayers who already advanced the chain under the higher rate but haven't yet claimed are underpaid for work already performed, which is an unfairness/incentive-misalignment issue but less severe than the fund-drain direction.

### Likelihood Explanation
Any account can act as a relayer for consensus messages — no special privilege is required to call the code path that credits rewards (`on_executed` → `process_message` → `calculate_reward`), only a valid signed `ConsensusMessage`. Governance rate changes via `update_cost_per_block` are a normal, expected operational action (adjusting incentives per state machine), not an attack; the bug is triggered by ordinary rate-tuning combined with a relayer's ordinary ability to choose submission timing, making the scenario realistically likely to occur during normal operation.

### Recommendation
Implement the accumulator/index pattern recommended in the referenced report: track a cumulative reward-per-block accumulator (or store the block height and its corresponding rate at every `update_cost_per_block` call), and compute a relayer's reward as the sum of `(height_range) * (rate_applicable_to_that_range)` across all rate changes since `baseline`, rather than a single multiplication by the current rate. At minimum, before mutating `StateMachinesCostPerBlock`, call `calculate_reward`/settle any pending unpaid span at the old rate (finalizing `LastRewardedHeight` up to the current `latest_height`) so that no unpaid span ever straddles a rate change.

### Proof of Concept
1. Governance sets `cost_per_block = 10` for `state_machine_id = X` via `update_cost_per_block`.
2. The chain advances from height 100 to height 200 for `X` via legitimate consensus updates, but no relayer submits a `ConsensusMessage` claiming the reward yet (`LastRewardedHeight` stays at 100).
3. Governance raises the rate to `cost_per_block = 1000` for `X` (e.g., to incentivize a different urgent update).
4. A relayer now submits (or resubmits/observes) a `ConsensusMessage` that results in a `StateMachineUpdated` event with `latest_height = 200`.
5. `calculate_reward` computes `blocks = 200 - 100 = 100` and multiplies by the *current* `block_cost = 1000`, paying `100,000` from the treasury instead of the `1,000` that would have been owed under the rate that was actually in effect for those 100 blocks — a 100x over-payment drained straight from `TreasuryAccount`. [6](#0-5)

### Citations

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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L92-99)
```rust
		let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);

		let blocks = latest_height.saturating_sub(baseline);

		let blocks_as_balance: <T as pallet_ismp::Config>::Balance = blocks.saturated_into();
		let reward = blocks_as_balance.saturating_mul(block_cost);

		Ok(reward)
```

**File:** modules/pallets/consensus-incentives/src/lib.rs (L70-79)
```rust
	// Mapping from state machineId to respective cost per block
	#[pallet::storage]
	#[pallet::getter(fn state_machines_cost_per_block)]
	pub type StateMachinesCostPerBlock<T: Config> = StorageMap<
		_,
		Blake2_128Concat,
		StateMachineId,
		<T as pallet_ismp::Config>::Balance,
		OptionQuery,
	>;
```

**File:** modules/pallets/consensus-incentives/src/lib.rs (L133-150)
```rust
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
