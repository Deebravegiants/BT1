### Title
Retroactive reward-rate application in `pallet-consensus-incentives` pays unsettled block-spans at the post-update `cost_per_block` - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`pallet-consensus-incentives` rewards relayers for delivering consensus proofs based on the number of un-rewarded blocks a proof advances a remote state machine, multiplied by a governance-configurable `cost_per_block`. The reward for the pending (unsettled) span is only computed lazily, at the moment a relayer's proof lands, using whatever `cost_per_block` is *currently* stored — not the rate(s) that were in effect while those blocks accrued. When governance calls `update_cost_per_block` to change the rate, there is no step that first settles the outstanding unrewarded span at the old rate. This is structurally identical to the BendDAO finding: a fee/rate parameter is changed without first accruing/settling the pending balance computed under the previous rate.

### Finding Description
The reward is computed in `calculate_reward`: [1](#0-0) 

`baseline` is the last-rewarded watermark (`LastRewardedHeight`), and `blocks = latest_height - baseline` is the entire unsettled span since the last payout — which can span an arbitrary number of blocks and, therefore, an arbitrary length of real time. The reward is `blocks * block_cost`, where `block_cost` is read fresh from `StateMachinesCostPerBlock` at claim time: [2](#0-1) 

Governance updates this rate via `update_cost_per_block`, which overwrites the stored value immediately and unconditionally — it does not force settlement of any pending span at the old rate first: [3](#0-2) 

Because `on_executed`/`process_message` (the `FeeHandler` hook) fires whenever a relayer's `ConsensusMessage` is processed by `pallet-ismp` — an ordinary, permissionless, unsigned extrinsic path — any relayer can trigger settlement of the entire unpaid span at whatever `cost_per_block` happens to be configured at delivery time, regardless of when within that span the blocks were actually produced/relayed-worthy.

### Impact Explanation
If governance raises `cost_per_block` (e.g., to reflect increased infrastructure costs going forward), any span of blocks that accrued under the old, lower rate but has not yet been claimed is paid out entirely at the new, higher rate — silently overpaying relayers from the shared `TreasuryAccount` for work that was priced lower when it was actually performed. Conversely, lowering the rate underpays relayers for blocks that accrued while the higher rate was in effect, permanently denying them the reward they were promised for that span (the "old" reward is never recoverable since only a single lump payment per span is made, keyed to the `LastRewardedHeight` watermark). Either direction is a direct treasury/fund-accounting fault: a mismatch between the reward rate in effect while liability accrued and the rate actually paid out.

### Likelihood Explanation
`update_cost_per_block` is expected to be called periodically by governance as market/infra costs change — it is a routine operational action, not a misuse of admin privilege (mirroring the BendDAO scenario, where `feeFactor` changes are also routine governance operations). Any relayer normally submits consensus proofs at irregular intervals, so there will almost always be an unsettled span outstanding when a rate change occurs, making the miscalculation window realistically hit on essentially every rate update.

### Recommendation
Before writing the new `cost_per_block`, force settlement of any outstanding unrewarded span using the *current* rate (i.e., compute and pay out the pending reward for `latest_height - baseline` at the old rate and advance `LastRewardedHeight`), analogous to accruing interest/fees before changing the rate in the BendDAO fix. Alternatively, record `(height, rate)` checkpoints so `calculate_reward` can integrate the correct historical rate over sub-spans instead of applying a single point-in-time rate to the whole unsettled interval.

### Proof of Concept
1. Governance sets `cost_per_block = 100` for state machine `X` via `update_cost_per_block`.
2. Over the next 1000 blocks, no relayer submits a consensus proof for `X` (span accrues unclaimed, `LastRewardedHeight` stays at old watermark).
3. Governance calls `update_cost_per_block` again, raising the rate to `1000` (a 10x increase, e.g. reflecting new infra costs going forward).
4. A relayer then submits a `ConsensusMessage` proof advancing `X`'s state machine height by the full 1000-block backlog.
5. `on_executed` → `process_message` → `calculate_reward` computes `reward = 1000 blocks * 1000 (current rate) = 1,000,000`, instead of the `100,000` that should have been owed for blocks that accrued entirely under the old rate.
6. The treasury pays out 10x the intended amount for that backlog, confirmed by `StateMachinesCostPerBlock::<T>::mutate` in `update_cost_per_block` [4](#0-3)  having no interaction with `LastRewardedHeight`/settlement logic in `impls.rs`.

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
