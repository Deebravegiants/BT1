Confirmed: no test or mechanism validates rate changes mid-backlog; `calculate_reward` always reads the *current* `StateMachinesCostPerBlock` and multiplies it by the entire unpaid span since `LastRewardedHeight`, exactly mirroring the BigBang debt-rate flaw.

### Title
Retroactive `cost_per_block` rate changes cause incorrect treasury reward payouts in `pallet-consensus-incentives` - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`pallet-consensus-incentives` rewards relayers for consensus proof delivery based on `reward = (latest_height - baseline) * cost_per_block`, where `baseline` is a watermark that only advances on payout. Whenever governance calls `update_cost_per_block` to change the rate via `modules/pallets/consensus-incentives/src/lib.rs`, the new rate is applied retroactively to the *entire* unpaid block span the next time any relayer submits a consensus message, including blocks that accrued under the old, different rate.

### Finding Description
`calculate_reward` in [1](#0-0)  computes the reward strictly from the current value of `StateMachinesCostPerBlock` at call time, multiplied by `blocks = latest_height.saturating_sub(baseline)`, where `baseline` is `LastRewardedHeight` (the last paid watermark), not the time/height at which the rate was last changed.

`update_cost_per_block` in [2](#0-1)  simply overwrites `StateMachinesCostPerBlock` for a state machine — it performs no settlement/accrual of the pending unpaid span at the old rate before applying the new one, and `LastRewardedHeight` is left untouched.

This is structurally identical to the referenced BigBang finding: interest/reward accrues linearly with elapsed "time" (here, block height), and a mid-period rate change is applied across the whole elapsed span rather than being split at the point of change, because there is no forced accrual/checkpoint on rate update.

### Impact Explanation
Because reward payout is triggered by `on_executed` whenever *any* relayer submits a `ConsensusMessage` (`FeeHandler::on_executed` in ), and the reward is paid straight out of `TreasuryAccount` via `T::Currency::transfer` in [3](#0-2) , an unprivileged relayer can manipulate payout size purely by choosing *when* to submit a proof relative to governance rate changes:

- If governance raises `cost_per_block` (e.g., due to rising infra costs), a relayer who has withheld submitting proofs for a large backlog of already-produced blocks is paid the new, higher rate for the entire historical backlog — an unintended/unbacked drain of the treasury beyond what governance intended to authorize for those old blocks.
- If governance lowers the rate, relayers who submit promptly are underpaid for blocks that should have earned the prior (higher) rate, and relayers who delay submission until just before a rate cut can front-run it to capture the old (higher) rate for blocks they hadn't yet delivered proofs for.

This is a treasury fund-accounting flaw reachable purely by relayer proof delivery (an unprivileged, permissionless action), and it directly causes miscalculated/unbacked treasury outflows.

### Likelihood Explanation
Any relayer that delays or times submission of a `ConsensusMessage` around a `update_cost_per_block` governance action naturally triggers this. There is no time-of-change checkpoint (no forced payout/reset of `LastRewardedHeight`, and no split calculation across the rate boundary), so the bug fires deterministically whenever cost_per_block is adjusted while any unpaid block-span backlog exists — which is the normal steady-state (only the most recently rewarded height is watermarked, not every intermediate height).

### Recommendation
When `update_cost_per_block` changes the rate for a state machine, first force settlement of the existing unpaid span at the *old* rate (i.e., compute and pay out `(latest_height - LastRewardedHeight)` at the current rate and advance the watermark) before storing the new rate, so no span is ever paid at a rate that didn't apply when those blocks were produced. Alternatively, persist the block-height (or block number) at which each rate took effect and split `calculate_reward`'s span calculation across rate-change boundaries, summing `Σ (blocks_in_segment_i * rate_i)`.

### Proof of Concept
1. Governance calls `update_cost_per_block(state_machine_id, 100)` — [4](#0-3) .
2. A relayer delivers consensus updates advancing the state machine height by, say, 40 blocks, but withholds calling `handle_unsigned` (i.e., doesn't submit the reward-triggering `ConsensusMessage` yet), so `LastRewardedHeight` stays at the old watermark.
3. Governance later raises the rate to `update_cost_per_block(state_machine_id, 1000)` believing it only applies going forward.
4. The relayer now submits the `ConsensusMessage`; `calculate_reward` computes `blocks = 40`, `reward = 40 * 1000` — 10x more than intended for the 40 blocks that were actually produced/relayed under the old 100-cost regime, drained directly from `TreasuryAccount` per [5](#0-4) .

### Citations

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

**File:** modules/pallets/consensus-incentives/src/lib.rs (L130-150)
```rust
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
