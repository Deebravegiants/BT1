### Title
Consensus-incentive reward baseline retroactively pays for blocks accrued before incentives were enabled - ([File: modules/pallets/consensus-incentives/src/impls.rs])

### Summary
`pallet-consensus-incentives::calculate_reward` computes a relayer's reward as `(latest_height - baseline) * block_cost`, where `baseline` falls back to `previous_commitment_height` whenever `LastRewardedHeight` has never been set for that state machine. `previous_commitment_height`/`latest_commitment_height` are updated by the core ISMP consensus handler on *every* `StateMachineUpdated` event, independent of whether reward accounting (`StateMachinesCostPerBlock`) was even enabled at the time. This is the same class of bug as the GMX funding-fee issue: a purely time/height-based accrual value that keeps advancing silently while "the paying side" (the treasury/incentive scheme) is not yet active, and then charges the *entire* backlog the instant the scheme becomes active — exactly like OI going from one side to two and the newly-arriving side being billed for the whole dormant period.

### Finding Description
`calculate_reward` in [1](#0-0)  reads:
```
let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);
let blocks = latest_height.saturating_sub(baseline);
let reward = blocks_as_balance.saturating_mul(block_cost);
```
`previous_height` comes from `host.previous_commitment_height`, which is simply the state machine's second-to-last committed height, tracked unconditionally by `store_latest_commitment_height` in [2](#0-1)  every time any consensus update lands for that state machine — whether or not `StateMachinesCostPerBlock` was set at the time.

`StateMachinesCostPerBlock` is a governance-controlled `OptionQuery` map (`update_cost_per_block` / `remove_incentives` in [3](#0-2) ). Nothing initializes `LastRewardedHeight` when `update_cost_per_block` is first called, nor when `remove_incentives` disables it. So the first time a relayer delivers a `StateMachineUpdated` event after incentives are (re-)enabled, `process_message` in [4](#0-3)  pays for the full span from `previous_commitment_height` to `latest_height` — a span that may include many blocks/updates that occurred while incentives were off (or before they were ever configured), i.e. periods during which no reward should have accrued at all.

This is precisely analogous to the GMX report: the code special-cases "not paying" while a condition doesn't hold (no `StateMachinesCostPerBlock` entry / no `LastRewardedHeight` watermark), but has no mechanism to record *when* that non-paying period ends, so once the paying condition is (re)established, the entire backlog — computed strictly from height/commitment bookkeeping that never paused — is billed in full to the treasury on the very next relayer submission.

### Impact Explanation
This mispriced reward is paid directly out of the treasury (`T::Currency::transfer(&TreasuryAccount, ...)`), and simultaneously mints `ReputationAsset` proportional to the same inflated amount. An attacker/relayer can:
1. Wait for a state machine whose light client has been advancing for a long time with `StateMachinesCostPerBlock` unset (or freshly removed via `remove_incentives`).
2. Wait for/trigger governance to set (or reset) `update_cost_per_block` for that chain.
3. Immediately submit the next consensus proof, collecting a reward sized to the entire historical block span since the last commitment update — not just the span that accrued under the active incentive — draining an amount from the treasury far larger than intended, and inflating their reputation-asset balance to match.

This is a concrete treasury drain / incorrect fund distribution triggered by an ordinary, unprivileged relayer action (submitting a consensus message), reachable via the standard `FeeHandler::on_executed` path invoked after ordinary message processing.

### Likelihood Explanation
Likelihood is moderate-to-high: it doesn't require any malicious governance action, only that a state machine's light client accrue height between the moment incentives are configured/reconfigured and the first post-configuration relayer submission — a normal, expected occurrence in production, and the existing rollback test in [5](#0-4)  demonstrates the team is aware baseline-vs-previous_height interactions are subtle, but that test only covers a rollback scenario, not the "incentives freshly enabled on an already-advanced chain" scenario.

### Recommendation
When `update_cost_per_block` transitions a state machine from unset to set (or after `remove_incentives` clears it), explicitly initialize `LastRewardedHeight` to the *current* `latest_commitment_height` at that moment, so the reward baseline starts from "now," not from whatever height happened to be recorded by unrelated consensus-update bookkeeping. Symmetrically, `remove_incentives` should either leave `LastRewardedHeight` untouched (which is fine) but `update_cost_per_block` must not rely on the stale `previous_commitment_height` fallback for chains with pre-existing commitment history.

### Proof of Concept
1. State machine `X` has been running with periodic `StateMachineUpdated` events (heights 100 → 5000) for a long time, with `StateMachinesCostPerBlock[X]` unset (no reward configured).
2. Governance calls `update_cost_per_block(X, cost=1000)` at height 5000. No `LastRewardedHeight` entry exists yet.
3. A relayer submits the next consensus proof, producing `StateMachineUpdated { state_machine_id: X, latest_height: 5010 }`.
4. `calculate_reward` computes `baseline = previous_commitment_height(X)` (e.g., 4990, the height before 5000) — NOT 5000 (the height at which the incentive was enabled).
5. `blocks = 5010 - 4990 = 20`, reward = `20 * 1000`, instead of the correct `5010 - 5000 = 10` blocks that actually accrued under the active incentive — the relayer is paid double (or, in a more extreme case where the chain hasn't updated for a long stretch pre-configuration, an arbitrarily larger multiple) what they should receive, drained straight from the treasury account.

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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L78-99)
```rust
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
```

**File:** modules/pallets/ismp/src/host.rs (L229-234)
```rust
	fn store_latest_commitment_height(&self, height: StateMachineHeight) -> Result<(), Error> {
		let previous_height = LatestStateMachineHeight::<T>::get(height.id).unwrap_or_default();
		PreviousStateMachineHeight::<T>::insert(height.id, previous_height);
		LatestStateMachineHeight::<T>::insert(height.id, height.height);
		Ok(())
	}
```

**File:** modules/pallets/consensus-incentives/src/lib.rs (L128-167)
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
