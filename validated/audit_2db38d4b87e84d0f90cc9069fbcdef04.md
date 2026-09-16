## Title
Consensus relayer rewards use the current `cost_per_block` for the entire unrewarded height span instead of prorating at the rate-change point - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`pallet-consensus-incentives` rewards relayers for delivering `ConsensusMessage`s based on how many blocks of a remote state machine's height the update advances, multiplied by a governance-configurable `cost_per_block`. Exactly like the M-32 finding in LoopFi's `ChefIncentivesController` (which applied the newest `rewardsPerSecond` over a duration that spanned an earlier, different rate), `calculate_reward` applies the *current* `cost_per_block` to the *entire* span between the last-rewarded watermark and the latest height, even when `cost_per_block` changed partway through that span via `update_cost_per_block`.

### Finding Description
`calculate_reward` computes: [1](#0-0) 

```rust
let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);
let blocks = latest_height.saturating_sub(baseline);
let blocks_as_balance: <T as pallet_ismp::Config>::Balance = blocks.saturated_into();
let reward = blocks_as_balance.saturating_mul(block_cost);
```

`block_cost` is read once, at call time, from `StateMachinesCostPerBlock` [2](#0-1) . It is a single scalar applied over the whole `blocks` interval `[baseline, latest_height]`. There is no record of *when* `cost_per_block` last changed, so if `update_cost_per_block` [3](#0-2)  is invoked between two relayer deliveries, the entire un-rewarded block span — including the portion that occurred under the *old* rate — is paid out at the *new* rate. This is the same formula error as M-32: the correct computation would be `oldCost * (changeHeight - baseline) + newCost * (latest_height - changeHeight)`, but the pallet instead computes `newCost * (latest_height - baseline)`.

The reward is paid unconditionally from the treasury to whichever relayer next submits a valid consensus message (an unprivileged, permissionless action — anyone can relay and submit a `ConsensusMessage` proof) via `process_message` -> `T::Currency::transfer` from `TreasuryAccount` [4](#0-3) .

### Impact Explanation
If governance raises `cost_per_block` (e.g., due to gas-price changes on the destination chain), the very next relayer to submit a consensus update is overpaid for the entire backlog of already-elapsed blocks that should have been priced at the old, lower rate — draining the treasury faster than intended and effectively minting unbacked rewards for blocks not actually costed at that rate. Conversely a rate decrease underpays legitimate relayers. Because delivery is permissionless and the reward is paid to "whichever account happens to relay next," this can be triggered opportunistically: a relayer can watch for (or race to be first after) a `cost_per_block` increase and capture inflated rewards for the whole unpaid backlog in one message, rather than only for blocks accrued after the change. This is a direct treasury-fund-loss vector, not merely a rounding/edge-case issue, since the backlog (`latest_height - baseline`) can be arbitrarily large if deliveries are infrequent.

### Likelihood Explanation
`update_cost_per_block` is a normal, expected operational lever (README explicitly documents it as the mechanism to "set or update the reward cost per block") [5](#0-4) , so rate changes are a routine, non-malicious operational path, not a hypothetical governance-abuse scenario. Any period of infrequent consensus updates followed by a rate change and then a delivery reproduces the overpayment deterministically — no exotic conditions are required, only a rate change during an unrewarded interval.

### Recommendation
Track the height (or timestamp) at which each `cost_per_block` change takes effect, and when computing `calculate_reward`, split the `[baseline, latest_height]` interval at each rate-change boundary, summing `cost_i * blocks_i` per segment — mirroring the corrected `oldRate*(t1-t0) + newRate*(now-t1)` formula recommended in the referenced report. Alternatively, force a reward settlement (flush pending rewards using the still-current rate) inside `update_cost_per_block` before the new rate is written, so no un-rewarded span ever spans two rates.

### Proof of Concept
1. Governance sets `cost_per_block = X` for `state_machine_id = S` via `update_cost_per_block`.
2. No relayer submits a consensus update for `S` for a long time, causing `latest_height` to run far ahead of `LastRewardedHeight` (e.g., due to low delivery incentive at rate `X`).
3. Governance raises the rate to `cost_per_block = Y` (`Y > X`) to attract relayers.
4. A relayer immediately submits a `ConsensusMessage` for `S`. `process_message` -> `calculate_reward` computes `reward = (latest_height - baseline) * Y`, paying the *entire* backlog at the new higher rate `Y`, instead of `X` for the pre-change blocks and `Y` only for the blocks after the change.
5. The relayer receives an inflated reward from `TreasuryAccount`, and `LastRewardedHeight` is advanced to `latest_height`, permanently losing the ability to correct the overpayment for that span.

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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L92-99)
```rust
		let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);

		let blocks = latest_height.saturating_sub(baseline);

		let blocks_as_balance: <T as pallet_ismp::Config>::Balance = blocks.saturated_into();
		let reward = blocks_as_balance.saturating_mul(block_cost);

		Ok(reward)
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

**File:** modules/pallets/consensus-incentives/README.md (L35-35)
```markdown
* `update_cost_per_block(origin, state_machine_id, cost_per_block)`: A privileged extrinsic used to set or update the reward cost per block for a given state machine.
```
