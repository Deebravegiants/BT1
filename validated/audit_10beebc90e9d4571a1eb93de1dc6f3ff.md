### Title
Consensus-incentive reward miscalculation on `update_cost_per_block` rate change – ([File: modules/pallets/consensus-incentives/src/lib.rs])

### Summary
`pallet-consensus-incentives::update_cost_per_block` changes the `StateMachinesCostPerBlock` reward rate for a state machine without first settling (paying out) the reward already accrued for the unpaid block span at the old rate. Because `calculate_reward` always applies the *current* rate to the entire unpaid span between the `LastRewardedHeight` watermark and the newly delivered height, a rate change retroactively repaces the reward for blocks that were actually relayed/finalized under the previous rate — the exact "share index" class of bug described in the external report, applied to the treasury→relayer reward stream instead of a farm's emission-based share index.

### Finding Description
`update_cost_per_block` simply overwrites the map entry: [1](#0-0) 

There is no call analogous to `increase_share_indexes` that would first accrue/settle the reward owed for the span already pending (from `LastRewardedHeight` up to the state machine's current commitment height) at the *old* `cost_per_block` before the rate is replaced.

The reward is only computed later, when a relayer actually submits a `ConsensusMessage` that advances the state machine, in `calculate_reward`: [2](#0-1) 

`block_cost` here is read fresh via `StateMachinesCostPerBlock::<T>::get(state_machine_id)` inside `process_message` at message-processing time — i.e., whatever the *current* rate is — and multiplied by the *entire* span `latest_height - baseline`, where `baseline` is the `LastRewardedHeight` watermark (or the previous commitment height if unset): [3](#0-2) 

Because the reward calculation does not track which portion of the span accrued under which rate, any block span that straddles a `update_cost_per_block` change is entirely priced at the new rate, not proportionally split between the old and new rate.

### Impact Explanation
This directly parallels the bug class in the external report: a rate/emission change that isn't preceded by settlement of previously-accrued shares/rewards causes the wrong amount to be paid out. Concretely on Hyperbridge:

- If governance raises `cost_per_block` (e.g. to better incentivize a state machine), any relayer holding an already-finalized-but-unsubmitted consensus proof can submit it *after* the rate increase and be paid the new, higher rate for blocks that were finalized (and should have been priced) under the old, lower rate. This is a direct, permissionless overpayment/drain from `T::TreasuryAccount` — the very account the pallet transfers from in `process_message` (`T::Currency::transfer(&T::TreasuryAccount::get()..., &relayer_account, reward, ...)`).
- Conversely, if the rate is lowered, honest relayers who already did the work of watching/proving blocks under the higher rate are underpaid, matching the "unfair distribution" impact called out in the external report.

This is a fund-accounting integrity issue reachable by any relayer through the fully permissionless `handle_unsigned` consensus-message submission path, not requiring a malicious admin — governance performing an ordinary, legitimate rate update is enough to create the window that a rational relayer can exploit by timing submission of an already-obtained proof.

### Likelihood Explanation
Likelihood is moderate-to-high: `update_cost_per_block` is an expected, routine governance operation (adjusting incentive economics per state machine), and relayers naturally batch/hold proofs before submitting them (network latency, congestion, or deliberate timing). Any relayer aware of an impending or just-executed rate change has a direct financial incentive to time submission of a pending consensus proof to capture the higher rate for a large already-elapsed span.

### Recommendation
Before mutating `StateMachinesCostPerBlock` in `update_cost_per_block`, settle the reward owed for the pending span at the *old* rate (mirroring `increase_share_indexes`): compute `blocks = latest_commitment_height - LastRewardedHeight` for the state machine using the outgoing `cost_per_block`, pay it out (or otherwise checkpoint it), advance `LastRewardedHeight` to the current height, and only then apply the new rate so future spans are calculated cleanly against a single rate.

### Proof of Concept
1. State machine `X` has `StateMachinesCostPerBlock[X] = 100` and `LastRewardedHeight[X] = 1000`.
2. A relayer submits (or has ready) a valid BEEFY/consensus proof that would advance `X`'s commitment height to 2000, but withholds submission.
3. Governance calls `update_cost_per_block(X, 1000)` to raise the per-block reward for future relaying (a legitimate, non-malicious governance action).
4. The relayer now submits the withheld proof via `pallet_ismp::handle_unsigned`, triggering `on_executed` → `process_message` → `calculate_reward`.
5. `calculate_reward` computes `blocks = 2000 - 1000 = 1000` and multiplies by the *current* `block_cost = 1000`, yielding a reward of `1,000,000` from the treasury — 10x what governance intended for that already-finalized span (`1000 * 100 = 100,000` under the old rate), because no settlement occurred at rate-change time.

### Citations

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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L41-59)
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
