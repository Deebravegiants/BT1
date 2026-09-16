## Title
`LastRewardedHeight` watermark is not reset when `remove_incentives` pauses and `update_cost_per_block` resumes consensus rewards, causing relayers to be overpaid for the paused span - (File: `modules/pallets/consensus-incentives/src/lib.rs`)

### Summary
`pallet-consensus-incentives` computes relayer rewards as `(latest_height - baseline) * cost_per_block`, where `baseline` is the `LastRewardedHeight` watermark from the last successful payout. When incentives for a state machine are disabled via `remove_incentives` and later re-enabled via `update_cost_per_block`, the watermark is never advanced during the "paused" interval, so the very next reward calculation pays out for the *entire* span since the last payment — including all the blocks that elapsed while incentives were supposed to be off. This mirrors the ZEAL `lastRewardBlock` bug class exactly: a pause/resume cycle fails to re-baseline the accrual pointer to "now," so rewards accrue for a period during which they should not.

### Finding Description
`StateMachinesCostPerBlock` acts as the pause/resume toggle: `remove_incentives` deletes the entry (pausing rewards for that state machine) and `update_cost_per_block` re-inserts it (resuming rewards). [1](#0-0) 

`process_message` only touches (and only advances) the `LastRewardedHeight` watermark inside the `if let Some(block_cost) = StateMachinesCostPerBlock::<T>::get(...)` branch: [2](#0-1) 

While `StateMachinesCostPerBlock` is `None` (i.e. after `remove_incentives`), `process_message` does nothing at all — no reward is paid, but critically the `LastRewardedHeight` watermark is also **not** advanced to the current chain height. It stays frozen at whatever it was before the pause.

`calculate_reward` then computes the reward span as `latest_height - baseline`, where `baseline` is that stale `LastRewardedHeight`: [3](#0-2) 

So the sequence is:
1. Cost per block is set (incentives active), relayers get paid up to height H1, `LastRewardedHeight = H1`.
2. Admin calls `remove_incentives` (pause). The chain's consensus state continues to advance (state machine heights climb) while no relayer is paid and the watermark stays at H1.
3. Admin later calls `update_cost_per_block` (resume) to re-enable rewards.
4. The next relayer to submit any `ConsensusMessage` — an entirely permissionless, unprivileged action reachable via `pallet_ismp::Pallet::handle_unsigned` → `on_executed` (the `FeeHandler` hook) — triggers `calculate_reward`, which computes `latest_height (H2) - baseline (H1)` and pays the *full* paused span, exactly as if incentives had been active the whole time.

This is the direct analog of the ZEAL report: emissions were "paused" but the accrual baseline (`lastRewardBlock` / `LastRewardedHeight`) was not advanced to "now" at pause time (or reset at resume time), so the paused interval is incorrectly included in the next payout calculation.

### Impact Explanation
The treasury pays out `$BRIDGE` and mints `ReputationAsset` for blocks during which incentives were explicitly disabled by governance/admin action, via `T::Currency::transfer` from the treasury and `T::ReputationAsset::mint_into`: [4](#0-3) 
This is an unbacked/erroneous reward payout — the treasury drains funds for a period where no reward was intended to accrue, and any relayer submitting the next consensus message after resumption captures this windfall. Depending on how long the pause lasts and the configured `cost_per_block`, this can be a substantial, unearned drain of the treasury's `$BRIDGE` balance, i.e. concrete loss of protocol funds.

### Likelihood Explanation
The trigger requires only a normal governance action sequence (disable then later re-enable incentives for a state machine — plausible for cost adjustments, incident response, or migrations) followed by a single, fully permissionless `handle_unsigned` consensus message submission by any relayer. No malicious admin or attacker collusion with governance is required; the bug fires automatically on the first post-resume consensus update. The existing test suite only covers rollback scenarios (`reward_covers_only_unpaid_heights_after_rollback`) and never exercises `remove_incentives` followed by `update_cost_per_block`, confirming this path is untested. [5](#0-4) 

### Recommendation
When resuming incentives — i.e., in `update_cost_per_block` (or whenever a previously-`None` `StateMachinesCostPerBlock` entry transitions to `Some`) — explicitly reset `LastRewardedHeight` for that `state_machine_id` to the current `latest_commitment_height`, so the newly resumed accrual only counts blocks going forward. Equivalently, `remove_incentives` could snapshot the current height into `LastRewardedHeight` at pause time so no gap accumulates regardless of how long the pause lasts.

### Proof of Concept
1. `update_cost_per_block(root, sm_id, 100)` — enable rewards, cost = 100/block.
2. Relayer submits a consensus message advancing the state machine to height 1000. Reward pays `(1000 - 0) * 100`; `LastRewardedHeight = 1000`.
3. `remove_incentives(root, sm_id)` — pause rewards.
4. State machine consensus continues to advance externally (e.g. via `store_latest_commitment_height`) to height 2000 while paused; no reward pays and `LastRewardedHeight` remains `1000`.
5. `update_cost_per_block(root, sm_id, 100)` — resume rewards.
6. Any relayer submits the next `ConsensusMessage` (`handle_unsigned` → `FeeHandler::on_executed` → `process_message` → `calculate_reward`). `baseline = LastRewardedHeight = 1000`, `latest_height = 2000` (or higher), so the relayer is paid `(latest_height - 1000) * 100`, fully covering the 1000-block paused interval that should have earned nothing.

### Citations

**File:** modules/pallets/consensus-incentives/src/lib.rs (L152-167)
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

**File:** modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs (L121-219)
```rust
#[test]
fn reward_covers_only_unpaid_heights_after_rollback() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		const BLOCK_COST: u128 = 100;
		let host = Ismp::default();
		let state_machine_id = setup_state_machine();
		let treasury_account: AccountId32 = PalletId(*b"treasury").into_account_truncating();

		pallet_consensus_incentives::Pallet::<Test>::update_cost_per_block(
			RuntimeOrigin::root(),
			state_machine_id,
			BLOCK_COST,
		)
		.unwrap();

		let (consensus_message, relayer_account) = setup_host_and_message(&host);
		let message = MessageWithWeight { message: consensus_message, weight: Weight::zero() };
		let updated = |height: u64| {
			vec![IsmpEvent::StateMachineUpdated(StateMachineUpdated {
				state_machine_id,
				latest_height: height,
			})]
		};

		// The chain has already advanced to 1025 and every block up to it has been rewarded once.
		host.store_state_machine_commitment(
			StateMachineHeight { id: state_machine_id, height: 1024 },
			commitment(),
		)
		.unwrap();
		host.store_latest_commitment_height(StateMachineHeight {
			id: state_machine_id,
			height: 1024,
		})
		.unwrap();
		host.store_state_machine_commitment(
			StateMachineHeight { id: state_machine_id, height: 1025 },
			commitment(),
		)
		.unwrap();
		host.store_latest_commitment_height(StateMachineHeight {
			id: state_machine_id,
			height: 1025,
		})
		.unwrap();

		let treasury_before_first = Balances::balance(&treasury_account);
		<pallet_consensus_incentives::Pallet<Test> as FeeHandler>::on_executed(
			vec![message.clone()],
			updated(1025),
		)
		.unwrap();

		assert_eq!(Balances::balance(&treasury_account), treasury_before_first - BLOCK_COST);
		assert_eq!(
			pallet_consensus_incentives::LastRewardedHeight::<Test>::get(state_machine_id),
			Some(1025)
		);

		// The previous-height pointer references an older height whose commitment is no longer
		// retained in the bounded map.
		pallet_ismp::PreviousStateMachineHeight::<Test>::insert(state_machine_id, 1);

		// Deleting the latest commitment rolls the latest height back to that previous pointer.
		host.delete_state_commitment(StateMachineHeight { id: state_machine_id, height: 1025 })
			.unwrap();
		assert_eq!(host.latest_commitment_height(state_machine_id).unwrap(), 1);

		// The next honest consensus update advances to 1030, carrying the stale pointer forward as
		// the new previous height.
		host.store_state_machine_commitment(
			StateMachineHeight { id: state_machine_id, height: 1030 },
			commitment(),
		)
		.unwrap();
		host.store_latest_commitment_height(StateMachineHeight {
			id: state_machine_id,
			height: 1030,
		})
		.unwrap();
		assert_eq!(host.previous_commitment_height(state_machine_id), Some(1));

		let treasury_before_second = Balances::balance(&treasury_account);
		<pallet_consensus_incentives::Pallet<Test> as FeeHandler>::on_executed(
			vec![message],
			updated(1030),
		)
		.unwrap();

		// The real advance is 1025 -> 1030, so only the 5 new blocks are paid rather than the full
		// span back to the previous pointer.
		assert_eq!(Balances::balance(&treasury_account), treasury_before_second - 5 * BLOCK_COST);
		assert_eq!(
			pallet_consensus_incentives::LastRewardedHeight::<Test>::get(state_machine_id),
			Some(1030)
		);
	})
}
```
