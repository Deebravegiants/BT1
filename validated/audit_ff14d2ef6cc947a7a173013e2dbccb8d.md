## Title
Stale `LastRewardedHeight` watermark causes unbacked treasury reward payout on consensus-incentives re-enablement - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
The `pallet-consensus-incentives`'s `process_message` function only advances the `LastRewardedHeight` watermark when a *non-zero* reward is actually paid out. When a state machine's `StateMachinesCostPerBlock` is unset or set to `0`, the watermark is never advanced while `latest_commitment_height` keeps climbing (driven by any relayer submitting consensus updates). Once cost-per-block is later set to a positive value, the very next processed message computes a reward spanning the *entire* frozen period and pays it as a lump sum from the treasury to whichever relayer happens to deliver that message — an unbacked, unintended treasury drain. This is directly analogous to the reported RAAC `tick()` bug, where `lastUpdateBlock` was not updated when `amountToMint` was `0`, causing a rate transition from `0` to a positive value to mint an inflated amount covering the entire idle interval.

### Finding Description
`calculate_reward` computes:
```rust
let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);
let blocks = latest_height.saturating_sub(baseline);
let reward = blocks_as_balance.saturating_mul(block_cost);
``` [1](#0-0) 

`process_message` only advances the watermark after paying a reward, and explicitly skips the update whenever the computed reward is zero:
```rust
if let Some(block_cost) = StateMachinesCostPerBlock::<T>::get(state_machine_id) {
    let reward = Self::calculate_reward(&state_machine_id, block_cost)?;
    if reward.is_zero() {
        return Ok(());
    }
    ...
    LastRewardedHeight::<T>::mutate(state_machine_id, |watermark| {
        *watermark = Some(watermark.unwrap_or_default().max(state_machine_height.height));
    });
}
``` [2](#0-1) 

If `StateMachinesCostPerBlock` for a given state machine is `None` (never configured, or removed via `remove_incentives`) or explicitly set to `0` via `update_cost_per_block`, then every call to `process_message` computes `reward == 0` and returns early without touching `LastRewardedHeight`, even though `latest_commitment_height` for that state machine keeps advancing independently through ordinary consensus updates (any relayer submitting `ConsensusMessage`s that trigger `StateMachineUpdated` events feeds this via `on_executed`):
```rust
for event in events {
    if let IsmpEvent::StateMachineUpdated(update) = event {
        highest_per_state_machine.entry(update.state_machine_id)...
    }
}
``` [3](#0-2) 

Governance can later call `update_cost_per_block` with a positive value to (re-)enable rewards for that state machine — a routine, non-malicious operational action:
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
    ...
}
``` [4](#0-3) 

Once re-enabled, the very next unprivileged relayer that delivers a `ConsensusMessage` causes `on_executed` → `process_message` → `calculate_reward` to compute `blocks = latest_height - baseline`, where `baseline` is still the stale, frozen watermark from before the zero-cost/unset period. This span includes every block that elapsed while rewards were disabled — work the current relayer did not necessarily perform — multiplied by the newly configured `cost_per_block`, producing an inflated lump-sum reward transferred out of `T::TreasuryAccount`.

### Impact Explanation
This causes an unbacked/incorrect payout from the protocol treasury (`TreasuryAccount`) to a single relayer, sized by however long the state machine's incentive was `0`/unset rather than by actual relaying work performed during that reward's active window. This is a concrete loss of treasury funds and an unfair/incorrect reward distribution, matching the "theft/loss of funds via incorrect reward accounting" impact class. The magnitude scales with how long the state machine goes without configured incentives (which can span from initial deployment, since `StateMachinesCostPerBlock` starts unset for every state machine, until an operator first configures it), making the windfall potentially very large on first activation.

### Likelihood Explanation
Medium: the vulnerable state (`StateMachinesCostPerBlock` unset or `0`) is not a hypothetical edge case — every state machine begins in this state before `update_cost_per_block` is first called, and operators may also legitimately pause incentives (`remove_incentives`) and later resume them. No malicious admin action is required; a normal enable/re-enable operational sequence combined with an ordinary relayer submitting the next consensus message triggers the bug.

### Recommendation
Advance `LastRewardedHeight` to `state_machine_height.height` on every processed update for a state machine regardless of whether `reward` is zero (analogous to always updating `lastUpdateBlock` in the RAAC fix), so the watermark tracks actual on-chain progress rather than only progress that happened to be rewarded. Alternatively, when (re-)configuring `StateMachinesCostPerBlock` via `update_cost_per_block`, reset `LastRewardedHeight` to the state machine's current `latest_commitment_height` so that no historical, unrewarded span is retroactively billed to the treasury.

### Proof of Concept
1. Deploy with a new state machine `X` for which `StateMachinesCostPerBlock` has never been set (or is set to `0`).
2. Over an extended period, relayers submit many `ConsensusMessage`s for `X`, advancing `latest_commitment_height` (via `IsmpHost::latest_commitment_height`) by, say, 100,000 blocks. `on_executed` → `process_message` runs each time but `StateMachinesCostPerBlock::get(X)` is `None`/`0`, so the `if let Some(block_cost)` branch is skipped or `reward.is_zero()` short-circuits — `LastRewardedHeight` for `X` is never set/advanced.
3. Governance calls `update_cost_per_block(X, cost_per_block)` with a positive `cost_per_block` (e.g. re-enabling incentives, an ordinary operation).
4. Any relayer submits one more `ConsensusMessage` for `X`, triggering `on_executed` → `process_message` → `calculate_reward`: `baseline` resolves to `previous_height` (or an old stale `LastRewardedHeight`), `blocks = latest_height - baseline ≈ 100,000`, and `reward = 100,000 * cost_per_block` is transferred from `TreasuryAccount` to that single relayer for work it did not perform.

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L46-74)
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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L89-99)
```rust
		// Use the rewarded watermark as the baseline and fall back to the previous height until
		// the first reward is recorded for this chain. The watermark only moves forward, so a
		// height that is rolled back and later resubmitted is not paid for a second time.
		let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);

		let blocks = latest_height.saturating_sub(baseline);

		let blocks_as_balance: <T as pallet_ismp::Config>::Balance = blocks.saturated_into();
		let reward = blocks_as_balance.saturating_mul(block_cost);

		Ok(reward)
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L133-145)
```rust
			let mut highest_per_state_machine: BTreeMap<StateMachineId, u64> = BTreeMap::new();
			for event in events {
				if let IsmpEvent::StateMachineUpdated(update) = event {
					highest_per_state_machine
						.entry(update.state_machine_id)
						.and_modify(|h| {
							if update.latest_height > *h {
								*h = update.latest_height;
							}
						})
						.or_insert(update.latest_height);
				}
			}
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
