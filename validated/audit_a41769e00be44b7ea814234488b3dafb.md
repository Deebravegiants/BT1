### Title
Flat `cost_per_block` applied retroactively to entire unclaimed height-span misattributes relayer rewards - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`pallet-consensus-incentives::calculate_reward` pays a relayer `(latest_height - baseline) * current_cost_per_block` for every consensus-update submission. The `cost_per_block` used is whatever value is currently stored in `StateMachinesCostPerBlock` at settlement time — there is no historical record of what the rate was for each individual block in the span. This is structurally the same flaw as the reported `UptimeTracker::computeValidatorUptime` bug: an aggregate quantity spanning multiple periods (blocks here, epochs there) is attributed a single rate/value without verifying what the correct per-unit rate/value actually was for each unit in that span.

### Finding Description
`Self::calculate_reward` computes the reward span as: [1](#0-0) 

```
let blocks = latest_height.saturating_sub(baseline);
let reward = blocks_as_balance.saturating_mul(block_cost);
```

`block_cost` is read once from `StateMachinesCostPerBlock::<T>::get(state_machine_id)` at `process_message` time: [2](#0-1) 

`StateMachinesCostPerBlock` is a single mutable value per state machine, freely updatable via the `update_cost_per_block` extrinsic: [3](#0-2) 

There is no per-block or per-period snapshot of the cost that applied historically. `baseline` (the last-rewarded watermark or the `previous_commitment_height`) can be arbitrarily far behind `latest_height` — a relayer's earlier consensus submission can leave a large un-rewarded block span if `process_message`'s `Currency::transfer` failed for that span, or if the relayer simply delays claiming (relayer submission of consensus proofs is unprivileged and permissionless, entered via `on_executed`/`FeeHandler`, itself invoked by dispatch of consensus `Message`s reachable by anyone). When the reward is finally computed, the *entire* span between `baseline` and `latest_height` is priced at whatever `cost_per_block` happens to be set **at the moment of settlement**, not the rate(s) that were actually in force block-by-block over that span.

This exactly mirrors the uptime bug's root cause: an aggregated interval (uptime-seconds / block-span) is redistributed onto sub-periods (epochs / blocks) using a uniform assumption (even split / current rate) instead of the actual per-sub-period ground truth (validator activity / historical cost).

### Impact Explanation
If governance changes `cost_per_block` (an expected, routine operation per the pallet's own `update_cost_per_block` extrinsic) while a relayer has an outstanding unrewarded block span:
- A relayer can strategically delay submitting/claiming a consensus update until after a rate increase, then collect the new, higher rate for blocks that were actually delivered/valid under the old, lower rate — draining excess funds from the treasury (`T::TreasuryAccount`) for work priced under a different regime.
- Conversely, if the rate decreases before an accumulated span is settled, honest relayers are underpaid for blocks delivered while the higher rate was in effect, discouraging relaying and reducing protocol reliability.

Either direction causes a direct mismatch between the value actually delivered per unit of work and the compensation paid, since `calculate_reward` has no way to price sub-ranges of the span differently — same class of "financial loss / unfair reward distribution" flagged in the original report, and it drains/misallocates the treasury (`Currency::transfer` in `process_message`), a real fund-accounting bug reachable through an ordinary, unprivileged relayer submission of a consensus message (the entry point that triggers `FeeHandler::on_executed` → `process_message` → `calculate_reward`).

### Likelihood Explanation
This requires only two ordinary, expected occurrences: (1) governance changing `cost_per_block` for an active state machine — an intended, exposed extrinsic used for legitimate fee tuning — and (2) any relayer that has (or engineers) an outstanding unpaid block span, achievable simply by waiting to submit the reward-triggering message until after a rate change, or by exploiting `RewardTransferFailed`/treasury underfunding to accumulate a large watermark gap before retrying. Since consensus message submission is fully permissionless and rate changes are a normal governance action (not malicious-governance/admin — the flaw is a bug in the pricing model, not requiring the admin to act maliciously), the likelihood of this occurring, intentionally or not, is Medium-to-High whenever rates are updated on a chain with any relaying backlog.

### Recommendation
Track cost-per-block changes with their effective height (e.g., a `Vec<(height, cost)>` or `StorageMap<height_range, cost>`), and compute `calculate_reward` by summing `blocks_in_range * cost_at_that_range` across every rate regime that overlaps `[baseline, latest_height]`, rather than applying a single current rate to the whole span. Alternatively, force settlement (or snapshot pending rewards) whenever `update_cost_per_block` is called, so no span can straddle two different rates.

### Proof of Concept
1. Governance calls `update_cost_per_block(state_machine_id, 100)`.
2. A relayer submits a consensus update advancing `latest_commitment_height` from height H to H+1000, but the reward transfer fails (e.g., treasury temporarily underfunded) — `LastRewardedHeight` is not advanced past the old watermark because `process_message` only updates the watermark after a successful transfer, so the 1000-block span remains outstanding.
3. Governance later raises `update_cost_per_block(state_machine_id, 10_000)` for unrelated market reasons.
4. Treasury is refunded; the relayer (or any relayer, since attribution is by whoever's signature is on the *next* consensus message) resubmits/triggers `on_executed` again with a message that produces a `StateMachineUpdated` event at height ≥ H+1000.
5. `calculate_reward` computes `blocks = 1000`, `block_cost = 10_000` (the new rate), paying `10_000_000` instead of the `100_000` that should have applied to blocks delivered under the old rate — a 100x overpayment drained from the treasury for work that was actually priced far lower when delivered. [4](#0-3)

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L41-47)
```rust
	fn process_message(
		state_machine_height: StateMachineHeight,
		state_machine_id: StateMachineId,
		relayer_account: T::AccountId,
	) -> Result<(), Error<T>> {
		if let Some(block_cost) = StateMachinesCostPerBlock::<T>::get(state_machine_id) {
			let reward = Self::calculate_reward(&state_machine_id, block_cost)?;
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L82-99)
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

		let blocks_as_balance: <T as pallet_ismp::Config>::Balance = blocks.saturated_into();
		let reward = blocks_as_balance.saturating_mul(block_cost);

		Ok(reward)
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
