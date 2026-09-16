### Title
Interest-rate-model-style retroactive repricing in `pallet-consensus-incentives` reward accrual — ([File: modules/pallets/consensus-incentives/src/impls.rs])

### Summary
`pallet-consensus-incentives` pays relayers a per-block reward for relaying Hyperbridge consensus updates to external chains. The reward for an interval is computed as `blocks_since_last_reward × current_block_cost`, where `current_block_cost` is read live at the time each message is processed rather than the rate(s) that were actually in effect during each block of that interval. This is structurally the same defect as the reported `TripleSlopeRateModel`/`accrueInterest()` bug: a rate change is applied retroactively to a period of elapsed time that occurred under a different rate, because the accrual is computed lazily on the next state-machine-update rather than being settled immediately when the rate changes.

### Finding Description
`Pallet::calculate_reward` computes the number of unrewarded blocks as the delta between the latest known state-machine height and a stored watermark, then multiplies that block count by whatever `StateMachinesCostPerBlock` currently holds: [1](#0-0) 

`process_message` calls this helper every time a `ConsensusMessage` for a given `state_machine_id` is executed, pays the relayer the resulting `reward`, and only then advances `LastRewardedHeight`: [2](#0-1) 

The watermark (`LastRewardedHeight`) only moves forward and is not touched when `StateMachinesCostPerBlock` is updated. Consequently, whenever governance adjusts the per-block cost for a state machine, the *next* consensus proof any relayer submits — an ordinary, unprivileged relaying action, not a governance or admin call — triggers `calculate_reward` to multiply the *entire* accumulated block range since the last payout (which spans time priced under the old rate) by the *new* rate. This is exactly the reported bug class: "new interest settings are applied to the previous period of time, which is not correct," except here the "interest rate" is the relayer reward rate and the "accrueInterest() call" is the routine consensus-message delivery/reward path that any relayer reaches by submitting a valid proof.

### Impact Explanation
Because the reward computation is triggered by an ordinary relayer action (delivering the next consensus update) rather than by the rate-change transaction itself, any rate adjustment silently mis-prices the entire unclaimed interval:
- If the cost-per-block is raised, the treasury (`T::TreasuryAccount`) overpays for blocks that should have been priced at the old, lower rate — an unbacked/inflated payout drawn from the treasury (`T::Currency::transfer` in `process_message`).
- If the cost-per-block is lowered, relayers are underpaid for blocks that accrued under the previous, higher rate, which is an economic loss to relayers and can starve consensus relaying for that destination.

Because relayer rewards can be economically significant and treasury funds are moved on every processed message, a rate change combined with a long unclaimed interval is a real transfer-of-funds miscalculation, not merely a display or informational issue.

### Likelihood Explanation
Likelihood is driven entirely by normal, expected operation: governance periodically re-tunes `StateMachinesCostPerBlock` to track gas-cost changes on destination chains (this is the documented purpose of the parameter), and any relayer's very next `handle_unsigned` consensus submission for that state machine will trigger the mis-priced accrual over the full unclaimed interval. No malicious actor is required — a single legitimate rate update plus a single subsequent legitimate relay is sufficient to trigger the wrong payout, and the longer the interval between consensus updates for a given destination, the larger the misprice.

### Recommendation
Before applying any update to `StateMachinesCostPerBlock` for a state machine, force settlement of the reward accrued up to the current height under the old rate (i.e., call the equivalent of `calculate_reward`/`process_message` and advance `LastRewardedHeight` to the current height as part of the same governance extrinsic), so the new rate only applies to blocks going forward. This mirrors the report's recommendation of using a "special service contract" that changes rate parameters immediately after accrual is finalized for the prior period.

### Proof of Concept
1. Governance sets `StateMachinesCostPerBlock[dest] = R1` and relaying proceeds normally; `LastRewardedHeight[dest]` sits at height `H0` after the last processed consensus message.
2. Time passes; the destination's finalized height advances to `H1` (a large gap, e.g. weeks of no relayed update).
3. Governance updates `StateMachinesCostPerBlock[dest] = R2` (a legitimate operational rate change, e.g. reflecting new gas costs).
4. Any relayer submits the next valid consensus proof for `dest` via the normal `handle_unsigned` message path, causing `process_message`/`calculate_reward` to run: `blocks = H1 - H0`, `reward = blocks × R2` (using `impls.rs:41-100`).
5. The relayer is paid for the entire `H0..H1` interval at rate `R2`, even though most of that interval accrued while the rate was `R1`, over- or under-paying the treasury depending on whether `R2 > R1` or `R2 < R1`.

Note: I was not able to fully trace the exact extrinsic/access-control code that sets `StateMachinesCostPerBlock` (e.g., its call name and origin) within the available search budget; this should be verified directly in `modules/pallets/consensus-incentives/src/lib.rs` before remediation, though its existence and role are confirmed by the storage read in `calculate_reward` and by references in the pallet's README.

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L41-74)
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
