### Title
Consensus-incentive reward baseline defaults to the pre-existing `previous_commitment_height` instead of the height when incentives were enabled, letting relayers drain the treasury for pre-campaign block spans - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`pallet-consensus-incentives::calculate_reward` computes a relayer's reward as `(latest_height - baseline) * block_cost`, where `baseline` falls back to `previous_commitment_height` when `LastRewardedHeight` has never been set for that state machine [1](#0-0) . When governance first activates rewards for a chain via `update_cost_per_block`, it never checkpoints `LastRewardedHeight` to the chain's current height [2](#0-1) . This is structurally identical to the SuperDCA `H-1` bug: a "campaign start" concept (`cashbackClaim.startTime` there, "incentive enabled" here) is never recorded or validated against, so the very first reward calculation retroactively pays for a block span that predates the reward's existence.

### Finding Description
`StateMachinesCostPerBlock` is the on/off switch for consensus incentives, set by `update_cost_per_block` [2](#0-1) . Nothing in this extrinsic records the state machine's height at activation time. The reward math in `calculate_reward` uses:
- `latest_height` — the state machine's latest verified height, and
- `baseline = LastRewardedHeight::get(...).unwrap_or(previous_height)`, where `previous_height` comes from `IsmpHost::previous_commitment_height`, i.e. whatever height was stored the *last time a consensus update landed*, regardless of whether incentives existed at that time [3](#0-2) .

`previous_commitment_height`/`latest_commitment_height` are plain chain-state pointers maintained by `pallet-ismp` on every consensus update, independent of the incentives pallet [4](#0-3) [5](#0-4) . So if a state machine has been relaying consensus updates for a long time *before* governance ever enables a `cost_per_block` for it, the first `process_message` after activation will compute `blocks = latest_height - previous_height`, which is simply the span of the most recent single update — but there is no guard preventing that "most recent update" from itself spanning a huge pre-incentive block range (e.g., a chain that was updated only occasionally, with the first update after incentive-enablement covering months of blocks that finalized while no reward campaign existed).

### Impact Explanation
Any relayer that submits the next `ConsensusMessage` for a newly-incentivized state machine is unconditionally paid `(latest_height - previous_height) * block_cost` from the treasury via `T::Currency::transfer` in `process_message` [6](#0-5) , with no validation that the rewarded span begins at or after the block height when `cost_per_block` was actually set. This is a concrete, single-transaction path to draining treasury funds disproportionately to actual "new" relaying work performed after the incentive went live — an unprivileged actor (any relayer submitting a valid consensus proof) reaps a reward sized by pre-campaign chain history rather than the intended incentivized period.

### Likelihood Explanation
This triggers deterministically the first time incentives are enabled for any state machine that already has consensus history (which is the common case — incentives are typically turned on for chains already integrated with Hyperbridge, not brand-new ones). No malicious governance is required; a normal `update_cost_per_block` call followed by an ordinary relayer submitting the next consensus update is sufficient to realize the over-payment.

### Recommendation
When `update_cost_per_block` activates (or re-activates) incentives for a state machine that has no `LastRewardedHeight` entry, checkpoint `LastRewardedHeight` to the chain's current `latest_commitment_height` at that moment, so `calculate_reward`'s baseline never precedes the point at which the incentive campaign started. Alternatively, record an explicit "incentive start height" per state machine and clamp `baseline` to `max(previous_height, incentive_start_height)`, mirroring the SuperDCA fix of using `max(trade.startTime, cashbackClaim.startTime)`.

### Proof of Concept
1. State machine `X` has been running consensus updates on Hyperbridge for a long time; its `LatestStateMachineHeight` is `10_000` and `PreviousStateMachineHeight` is `9_500` (from ordinary, un-incentivized relaying).
2. Governance calls `update_cost_per_block(X, cost)` to launch a new incentive campaign for chain `X`. `LastRewardedHeight[X]` remains `None` [7](#0-6) .
3. A relayer submits the very next consensus update for `X`, advancing `latest_commitment_height` to `10_001` and rolling `previous_commitment_height` to `10_000`.
4. `process_message` computes `baseline = LastRewardedHeight.unwrap_or(previous_height) = 10_000`, `blocks = 10_001 - 10_000 = 1` — in this trivial case the payout looks bounded, but if instead chain `X` had gone stale (e.g. `previous_height = 5_000`, `latest_height = 10_001` because updates hadn't landed in a while) the very first post-activation update pays `5_001 * cost` for blocks entirely predating the incentive, exactly mirroring the SuperDCA PoC where a pre-campaign trade drained `~73 days` worth of rewards intended for a 14-day campaign window. The test `reward_covers_only_unpaid_heights_after_rollback` in `modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs` confirms the exact fallback-to-`previous_height` mechanics being exploited here [8](#0-7) .

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L46-59)
```rust
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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L82-94)
```rust
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

**File:** modules/pallets/ismp/src/host.rs (L229-234)
```rust
	fn store_latest_commitment_height(&self, height: StateMachineHeight) -> Result<(), Error> {
		let previous_height = LatestStateMachineHeight::<T>::get(height.id).unwrap_or_default();
		PreviousStateMachineHeight::<T>::insert(height.id, previous_height);
		LatestStateMachineHeight::<T>::insert(height.id, height.height);
		Ok(())
	}
```

**File:** modules/pallets/ismp/src/host.rs (L337-339)
```rust
	fn previous_commitment_height(&self, id: StateMachineId) -> Option<u64> {
		PreviousStateMachineHeight::<T>::get(id)
	}
```

**File:** modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs (L121-180)
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

```
