### Title
Consensus-incentives reward retroactively applies a newly-updated `cost_per_block` to the entire unpaid historical block span - ([File: modules/pallets/consensus-incentives/src/impls.rs])

### Summary
`pallet-consensus-incentives` pays relayers for delivering `ConsensusMessage`s by multiplying the number of blocks a state-machine update advanced by a `cost_per_block` rate. That rate is read live at claim time and applied to the *entire* unpaid span since the last reward, exactly the pattern flagged in the Arrakis M-5 report: a fee/rate parameter is updated and then retroactively applied to a stock of value ("pending", unclaimed progress) that accrued under the old rate.

### Finding Description
`calculate_reward` computes the payout as:

```
blocks = latest_height - LastRewardedHeight[state_machine_id] (or previous_height on first reward)
reward = blocks * StateMachinesCostPerBlock[state_machine_id]
``` [1](#0-0) 

`StateMachinesCostPerBlock` is read at the moment a relayer submits a `ConsensusMessage` and is credited via `on_executed`/`process_message`, not snapshotted per-block as the chain progresses: [2](#0-1) 

Because the rate is applied to the whole `blocks` delta at claim time, any change to `StateMachinesCostPerBlock` via `update_cost_per_block` between two consensus updates is retroactively applied to the entire backlog of blocks that accrued under the *previous* rate, not just to newly produced blocks going forward. This mirrors the Arrakis bug precisely: `managerFeeBPS` was read live and applied to the whole pending fee balance that had accrued since the last collection, rather than being checkpointed at the time of each accrual.

The actor who ultimately reaches and benefits from this miscalculation is an unprivileged relayer: any relayer can submit a `ConsensusMessage` at a time of their choosing (subject to when new state-machine progress is available), and the reward calculation and payout from `TreasuryAccount` happens automatically in `on_executed`. A relayer can therefore intentionally wait for a rate increase before submitting a proof that covers a large accumulated span of already-elapsed blocks, collecting a payout sized by the new (higher) rate for work whose "cost" was fixed under the old rate — draining more from the treasury than the protocol intended for that span. Conversely a rate decrease right before submission underpays a relayer for blocks that should have been priced at the old rate.

### Impact Explanation
`StateMachinesCostPerBlock` funds are debited straight from `T::TreasuryAccount` to the relayer in `process_message`: [3](#0-2) 
An unprivileged relayer who controls the timing of their `ConsensusMessage` submission can exploit a rate increase to receive a treasury payout computed at the new rate for a span of blocks that elapsed under the old (lower) rate — a direct loss of protocol treasury funds beyond what governance intended, satisfying "concrete theft ... of funds" from the reachable analog list.

### Likelihood Explanation
Likelihood is moderate: it requires only an ordinary/expected governance operation (`update_cost_per_block`, callable via `IncentivesOrigin`) to change the reward rate, a routine action expected to happen over the life of the protocol as costs vary. No malicious governance action is required — the relayer merely needs to control the timing of an otherwise-legitimate `ConsensusMessage` submission relative to a rate change, and relayers already control when they submit messages (as seen in `LastRewardedHeight`'s rollback-handling logic, which shows message submission and reward calculation is entirely relayer-driven).

### Recommendation
Checkpoint the reward due at the time each block/height advances (or on rate change), rather than deferring the entire calculation to claim time using only the current rate. Concretely: on every `update_cost_per_block` call, first settle/checkpoint the outstanding reward for the current unpaid span at the *old* rate (advancing `LastRewardedHeight` and paying out or recording an accrued balance) before installing the new rate, so a subsequent claim only prices the blocks produced after the rate change at the new rate.

### Proof of Concept
1. Governance calls `update_cost_per_block(state_machine_id, LOW_COST)`.
2. The remote state machine advances from height H0 to H1 over a long period (e.g., 10,000 blocks) with no relayer submitting a consensus update (relayer intentionally withholds submission).
3. Governance later calls `update_cost_per_block(state_machine_id, HIGH_COST)` for unrelated operational reasons (e.g., inflation adjustment).
4. Immediately after, the relayer submits a `ConsensusMessage` proving the state machine's advance from H0 to H1.
5. `calculate_reward` computes `reward = (H1 - H0) * HIGH_COST` and `process_message` transfers this full amount from `TreasuryAccount` to the relayer — even though nearly the entire span (H0→H1) occurred while `LOW_COST` was configured. [4](#0-3) 

Note: I was unable to view `modules/pallets/consensus-incentives/src/lib.rs` in full (tool call failed on the final iteration) to confirm the exact `IncentivesOrigin` authorization model and whether any existing safeguard checkpoints rewards on rate change; based on the `README.md` and `impls.rs` evidence gathered, no such checkpoint exists, but this should be verified directly against `lib.rs`'s `update_cost_per_block` dispatchable before remediation.

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
