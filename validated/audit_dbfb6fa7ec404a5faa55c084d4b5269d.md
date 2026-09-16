### Title
`update_cost_per_block` retroactively re-prices the entire unpaid block span, letting a rate change over/under-pay consensus relayers for blocks already "owed" at the old rate - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`pallet-consensus-incentives::calculate_reward` computes `reward = (latest_height - baseline) * block_cost` using **only the currently-configured** `StateMachinesCostPerBlock` rate, without any per-height checkpointing of historical rates. If governance calls `update_cost_per_block` while there is an outstanding unpaid span (`LastRewardedHeight` behind `latest_commitment_height`), the very next relayer to deliver a consensus update is paid for the *entire* unpaid span at the *new* rate rather than a blend of the rate(s) in effect while those blocks accrued. This mirrors the JOJO `updateBorrowFeeRate` finding: a global, un-checkpointed rate variable is retroactively applied across an accrual window that spans a rate change.

### Finding Description
`StateMachinesCostPerBlock` stores a single current rate per state machine, updatable at any time via the privileged-but-ordinary `update_cost_per_block` extrinsic [1](#0-0) .

Reward accrual is watermarked by `LastRewardedHeight`, advanced only when a reward is actually paid [2](#0-1) . The reward calculation reads the **current** `block_cost` and multiplies it by the entire unpaid span from the watermark to `latest_height`: [3](#0-2) 

There is no mechanism that snapshots the rate at each height or splits the span at the point the rate changed — exactly the pattern in the JUSD report where `t0Rate`/`lastUpdateTimestamp` are reset without accounting for the interest that had already accrued at the old rate over the elapsed window.

Because relaying consensus updates for a given state machine is not required to happen every block (a relayer may batch, or nobody may relay for a while if there's no urgent traffic), it's easy for a real, non-malicious gap to open between `LastRewardedHeight` and the chain's actual `latest_commitment_height`. If `IncentivesOrigin` performs a routine rate adjustment (raising `cost_per_block` to reflect gas/market conditions) during that gap, the next relayer to submit a `ConsensusMessage` collects the reward for the *entire* accumulated span (old-rate blocks + new-rate blocks) priced entirely at the new, higher rate.

### Impact Explanation
This is a treasury drain vector reachable by an ordinary, unprivileged relayer (the entity submitting the `ConsensusMessage` via `pallet_ismp::handle_unsigned`/dispatch), not by governance itself: governance's action is a legitimate parameter update, but the resulting overpayment is realized and collected by whichever relayer happens to submit next. `T::Currency::transfer` moves the inflated amount straight out of `TreasuryAccount` [4](#0-3) , and an equivalent amount of `ReputationAsset` is also minted [5](#0-4) . A relayer with visibility into an upcoming rate increase (or simply one who is slow/batches deliveries) can capture a windfall proportional to `unpaid_blocks * (new_rate - old_rate)`, directly draining treasury funds beyond what governance intended to pay for that span. Conversely, a rate decrease under-pays relayers for blocks that were priced at the higher rate when delivered, which disincentivizes timely relaying but is a lesser-severity effect.

### Likelihood Explanation
Likelihood is moderate: it requires (1) an existing unpaid span (`LastRewardedHeight < latest_commitment_height`), which is common whenever relaying isn't perfectly synchronous with every state machine update, and (2) a `update_cost_per_block` call in between, which is a normal, expected governance operation (not an attack). No malicious admin behavior is needed — only an ordinary rate update landing while a backlog exists, which any relayer can then exploit or passively benefit from by being the one to submit the next proof.

### Recommendation
Checkpoint accrual so that a rate change cannot be applied retroactively to already-elapsed but unpaid blocks:
- On `update_cost_per_block`, force a reward flush for the current watermark-to-latest span at the old rate before changing the rate (i.e., pay/settle first, then update), or
- Store `(height, rate)` breakpoints and compute `calculate_reward` as a sum over sub-spans, each priced at the rate that was active during that sub-span, or
- Simplest: require `remove_incentives`/`update_cost_per_block` to first drain the pending reward for every affected state machine using the pre-change rate.

### Proof of Concept
1. Governance sets `StateMachinesCostPerBlock[SM] = 100` via `update_cost_per_block`.
2. Chain `SM` advances consensus commitments from height 1000 to height 2000 with no relayer submitting a reward-triggering `ConsensusMessage` in between (`LastRewardedHeight` stays at 1000, `latest_commitment_height` becomes 2000) — this is realistic since reward accrual only advances on message delivery, not on every height change (see the existing rollback test confirming the watermark/backlog semantics: `modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs` lines 118–219, especially the `reward_covers_only_unpaid_heights_after_rollback` test which demonstrates a large unpaid span being paid in one shot).
3. Before any relayer submits, governance legitimately raises the rate: `update_cost_per_block(SM, 10_000)`.
4. A relayer now submits a `ConsensusMessage` advancing to height 2000. `calculate_reward` computes `blocks = 2000 - 1000 = 1000`, `reward = 1000 * 10_000 = 10_000_000`, instead of the intended `1000 * 100 = 100_000` that should have applied to that already-elapsed backlog. The relayer collects a 100x windfall from the treasury for blocks that accrued entirely under the old, cheaper rate.

### Citations

**File:** modules/pallets/consensus-incentives/src/lib.rs (L81-86)
```rust
	/// The highest height a relayer has already been paid for, per state machine. Rewards only
	/// ever cover the span above this watermark, so a height that is revisited after a rollback
	/// is not paid for twice.
	#[pallet::storage]
	pub type LastRewardedHeight<T: Config> =
		StorageMap<_, Blake2_128Concat, StateMachineId, u64, OptionQuery>;
```

**File:** modules/pallets/consensus-incentives/src/lib.rs (L128-150)
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
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L53-59)
```rust
			T::Currency::transfer(
				&T::TreasuryAccount::get().into_account_truncating(),
				&relayer_account,
				reward,
				Preservation::Expendable,
			)
			.map_err(|_| Error::<T>::RewardTransferFailed)?;
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L67-68)
```rust
			T::ReputationAsset::mint_into(&relayer_account, reward.saturated_into())
				.map_err(|_| Error::<T>::ReputationMintFailed)?;
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
