## Title
Reward reactivation after `remove_incentives` pays out the entire unpaid backlog to a single unprivileged relayer - (File: `modules/pallets/consensus-incentives/src/lib.rs`)

### Summary
`pallet-consensus-incentives` rewards relayers for advancing a state machine's consensus height, gated by `StateMachinesCostPerBlock` and tracked via a monotonic `LastRewardedHeight` watermark. `remove_incentives` clears the cost-per-block configuration but never clears the `LastRewardedHeight` watermark. When incentives are later re-enabled with `update_cost_per_block`, the reward calculation still uses the old, stale watermark as its baseline, so the very next unsigned `ConsensusMessage` submitted by any relayer retroactively pays out the entire span of blocks that advanced while incentives were intentionally disabled — draining the treasury for work that was never meant to be compensated.

### Finding Description
`update_cost_per_block` and `remove_incentives` mutate only `StateMachinesCostPerBlock`; neither touches `LastRewardedHeight`: [1](#0-0) 

The reward for a processed `ConsensusMessage` is computed as `(latest_height - baseline) * cost_per_block`, where `baseline` falls back to `previous_height` only if `LastRewardedHeight` was never set; otherwise it uses the persisted (potentially very stale) watermark: [2](#0-1) 

`process_message` only advances `LastRewardedHeight` when `StateMachinesCostPerBlock` is `Some`, i.e. while incentives are enabled: [3](#0-2) 

Sequence that triggers the bug:
1. Incentives are enabled for a state machine (`update_cost_per_block`); `LastRewardedHeight` gets set to some height `H1` as relaying proceeds normally.
2. Governance calls `remove_incentives` for operational reasons (e.g. temporary pause). `StateMachinesCostPerBlock` is cleared, but `LastRewardedHeight` still equals `H1`.
3. While incentives are off, the chain's state machine height advances for free from `H1` to some much larger `H2` via ordinary (unpaid, and correctly so) consensus updates. No relayer is compensated — as intended.
4. Governance calls `update_cost_per_block` to re-enable incentives with a new rate.
5. Any single relayer — permissionlessly, via `pallet_ismp::handle_unsigned` submitting a further `ConsensusMessage` — triggers `on_executed`/`calculate_reward`. `baseline` resolves to the stale `H1` (not `H2`, the height at re-enable time), so `reward = (latest_height - H1) * cost_per_block` — the *entire* unpaid backlog is paid out to whichever relayer happens to submit first.

This is the same root-cause class as the referenced Angle `SavingsVest` finding: a parameter/state transition (disabling/re-enabling the incentive) does not settle or reset the accrual checkpoint before the new configuration takes effect, so a later, unrelated action retroactively applies to a period it should not cover.

### Impact Explanation
The exploit path requires no privileged access: the actor that captures the inflated reward is simply the first relayer to submit any subsequent `ConsensusMessage` for that state machine after re-enable — an ordinary, permissionless, unsigned extrinsic dispatch. The payout is a real `T::Currency::transfer` from the treasury plus a `ReputationAsset::mint_into`, both proportional to the entire unpaid backlog rather than the actual work done in that single message. Depending on how long incentives were disabled and the configured `cost_per_block`, this can drain a disproportionate, unbacked amount of `$BRIDGE` from the treasury to a single relayer — a direct loss of protocol funds triggered by an unprivileged action, matching the "unbacked mint / theft of funds" impact bar.

### Likelihood Explanation
Pausing and later resuming per-chain incentives via `remove_incentives`/`update_cost_per_block` is an ordinary, documented governance operation (e.g. during maintenance, cost re-tuning, or chain reconfiguration), not a malicious act. Once that ordinary sequence occurs, exploitation only requires an unprivileged relayer to be the first to submit a consensus proof afterward — something that happens naturally and immediately in normal operation, since relaying is competitive and permissionless. No special conditions or race beyond "be first after re-enable" are needed.

### Recommendation
When toggling incentive configuration for a state machine, settle the accrual checkpoint against the current chain height rather than leaving it stale:
- In `remove_incentives`, reset `LastRewardedHeight` to the state machine's current `latest_commitment_height` (or remove it entirely) so that no backlog can accumulate while incentives are off.
- In `update_cost_per_block`, when transitioning from `None` to `Some` (first enable or re-enable), similarly reset/initialize `LastRewardedHeight` to the current height before applying the new rate, so rewards only accrue for blocks advanced under the newly active configuration.

### Proof of Concept
1. Governance: `update_cost_per_block(sm, cost=C1)`. A relayer submits a `ConsensusMessage` advancing `sm` to height `H1`; `LastRewardedHeight::<T>::get(sm) == Some(H1)`.
2. Governance: `remove_incentives(sm)` — `StateMachinesCostPerBlock::<T>::get(sm) == None`, `LastRewardedHeight` untouched at `H1`.
3. Over time, several honest, unpaid `ConsensusMessage`s advance `sm`'s `latest_commitment_height` from `H1` to `H2` (large gap), as verified by `pallet_consensus_incentives::tests::skip_incentivizing_of_relayer_when_cost_per_block_is_not_set` confirming no reward/watermark update occurs while cost-per-block is unset: [4](#0-3) 
4. Governance: `update_cost_per_block(sm, cost=C2)`.
5. Any relayer submits one more `ConsensusMessage` advancing `sm` to `H2+1`. `on_executed` → `process_message` → `calculate_reward` computes `baseline = LastRewardedHeight::get(sm).unwrap_or(previous_height) == H1` and pays `reward = (H2+1 - H1) * C2` — the entire unpaid `H1..H2` span plus the new increment, transferred from the treasury to this single relayer, even though `H1..H2` was explicitly configured to be unincentivized.

### Citations

**File:** modules/pallets/consensus-incentives/src/lib.rs (L128-166)
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

**File:** modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs (L221-236)
```rust
#[test]
fn skip_incentivizing_of_relayer_when_cost_per_block_is_not_set() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		let host = Ismp::default();
		let (consensus_message, relayer_account) = setup_host_and_message(&host);

		pallet_ismp::Pallet::<Test>::handle_unsigned(
			RuntimeOrigin::none(),
			vec![consensus_message],
		)
		.unwrap();

		assert_eq!(Balances::balance(&relayer_account), UNIT);
	})
}
```
