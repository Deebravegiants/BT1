### Title
Stale reward watermark lets `update_cost_per_block` overpay backlogged blocks at the new rate - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`pallet-consensus-incentives` rewards the relayer that delivers a consensus update, paying `(latest_height - baseline) * cost_per_block` from the treasury. When `cost_per_block` is `0`, the pallet skips advancing its `LastRewardedHeight` watermark. If governance later raises `cost_per_block` to a non-zero value, the next relayer to submit a consensus message is paid for the *entire* block span that accrued while the rate was zero, at the new (higher) rate — an unintended treasury drain caused by exactly the same "rate changed but time/height anchor not reset" bug class described in the external report.

### Finding Description
`update_cost_per_block` lets `HostExecutiveOrigin`/`IncentivesOrigin` set the per-block reward rate for a state machine at any time, with no side effects on `LastRewardedHeight`: [1](#0-0) 

Reward calculation in `process_message`/`calculate_reward` uses `LastRewardedHeight` (or, if unset, `previous_commitment_height`) as the baseline for the reward span: [2](#0-1) 

Critically, when the computed `reward` is zero (which happens whenever `cost_per_block` is `0`), `process_message` returns **before** mutating `LastRewardedHeight`: [3](#0-2) 

So while `cost_per_block == 0`, every honest relayer message advances the chain's `latest_commitment_height` on Hyperbridge (via `update_client`), but `LastRewardedHeight` stays frozen at whatever height it last was when a non-zero reward was paid (or at the very first `previous_height` snapshot if no reward was ever paid). This is unbounded in duration — governance can leave `cost_per_block` at `0` for an arbitrary length of time.

When governance later sets `cost_per_block` back to a non-zero value, the very next relayer to submit a `ConsensusMessage` triggers `calculate_reward` with `baseline = LastRewardedHeight` (the old, stale height), so `blocks = latest_height - baseline` covers the *entire* dormant period plus the new blocks, and the reward is `blocks * new_cost_per_block` — paid in full from the treasury: [4](#0-3) 

This mirrors the reported `setManagementFeeBps()` bug precisely: a rate is changed by governance, but the "last accounted" anchor is not reset/advanced during the period the rate was inert, so the next accrual event is charged the full elapsed duration at the new rate instead of only the post-change duration.

### Impact Explanation
Any relayer submitting the first `ConsensusMessage` after governance raises `cost_per_block` from `0` back to a positive value collects a single lump-sum reward sized to the *entire* dormant block span (which can be arbitrarily large — weeks or months of blocks) multiplied by the new rate, rather than just the blocks produced after the rate change. This drains the `TreasuryAccount` of funds the protocol never intended to pay for that period, a direct loss of protocol funds triggered by an ordinary, permissionless relayer action (`handle_unsigned` submitting a consensus proof). Severity is Medium: it requires a specific but realistic governance sequence (temporarily zeroing, then re-enabling, the reward rate — a normal operational lever) and its payout is bounded by treasury balance, but it is a concrete overpayment of treasury funds to whichever relayer happens to deliver first.

### Likelihood Explanation
`update_cost_per_block` is a documented, expected governance action ("pass `0` to disable [rewards]" is the intended off-switch pattern used identically in the sibling `pallet-messaging-incentives`). Re-enabling incentives after a pause is a normal operational scenario, not an edge case. Any relayer racing to deliver the next consensus update after such a re-enable — or a relayer that deliberately delays submission until after they observe the rate increase — captures the inflated reward, requiring only the ordinary permissionless `handle_unsigned` extrinsic.

### Recommendation
When `cost_per_block` transitions to `0` (or is queried as zero) and there is no reward to pay, still advance `LastRewardedHeight` to the current `latest_height` so no block span is left to accrue "for free" and later be paid at a different rate. Equivalently, snapshot/reset `LastRewardedHeight` to the current latest height inside `update_cost_per_block` (and `remove_incentives`) whenever the rate changes, so a subsequent reward is always computed only over blocks produced under the new rate.

### Proof of Concept
1. Governance calls `update_cost_per_block(state_machine, 100)`; a relayer delivers a consensus update at height `H0` — `LastRewardedHeight = H0`, relayer paid `(H0 - previous) * 100`.
2. Governance calls `update_cost_per_block(state_machine, 0)` (pause incentives).
3. Over the next `N` blocks/consensus updates (arbitrarily long), relayers keep delivering proofs; `latest_commitment_height` advances to `H0 + N`, but every call to `process_message` computes `reward = blocks * 0 = 0` and returns before touching `LastRewardedHeight`, which stays at `H0`.
4. Governance calls `update_cost_per_block(state_machine, 1000)` to resume incentives at a higher rate.
5. The next relayer submits any `ConsensusMessage` advancing the height to `H0 + N + 1`. `calculate_reward` computes `blocks = (H0 + N + 1) - H0 = N + 1` and pays `reward = (N + 1) * 1000` from the treasury in one transfer — covering the entire dormant span `N` at the new rate, instead of `1` block, draining far more from `TreasuryAccount` than governance intended.

### Citations

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
