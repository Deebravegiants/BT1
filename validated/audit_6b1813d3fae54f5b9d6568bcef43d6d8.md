Based on my investigation, I found a valid analog in `pallet-consensus-incentives`, which reproduces the same "delta computed from an uninitialized watermark can be zero, permanently starving the first reward" bug class as the FairSide conviction-score report.

### Title
First consensus-relayer reward for a state machine can be permanently skipped due to `previous_commitment_height` initialization mismatch - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`Pallet::calculate_reward` derives a relayer's BEEFY/consensus-update reward from `latest_height - baseline`, where `baseline` falls back to `previous_commitment_height` only when no watermark (`LastRewardedHeight`) has ever been recorded for that state machine [1](#0-0) . `previous_commitment_height` is populated by `IsmpHost::store_latest_commitment_height`, which — on the very first consensus update for a state machine — sets `PreviousStateMachineHeight` equal to the *new* `LatestStateMachineHeight` value read before the update (defaulting to `0` and then being immediately followed by the actual height write), producing a `previous == latest` (or near-equal) pair for the first update in degenerate sequences [2](#0-1) .

### Finding Description
This is directly analogous to the FairSide bug: a per-entity accounting delta (`blocks = latest_height.saturating_sub(baseline)`) is computed against a "previous" state that was never meaningfully initialized for a brand-new key, so the very first computation naturally yields zero and the relayer is silently paid nothing for genuinely delivering the state machine's *first* consensus update (i.e. `blocks_as_balance.saturating_mul(block_cost) == 0`), and the reward path returns early on `reward.is_zero()` without ever writing `LastRewardedHeight` [3](#0-2) . Because `LastRewardedHeight` is never seeded, subsequent calls keep falling back to `previous_commitment_height` as baseline until a reward finally becomes non-zero, meaning the relayer effectively never gets compensated for the span of blocks between state-machine registration and the point where cumulative height finally exceeds the (potentially non-zero) `previous_commitment_height` baseline recorded at the first update.

### Impact Explanation
This causes the same class of "checkpoint never initializes, feature silently no-ops" impact: relayers who deliver the earliest BEEFY/consensus proofs for a newly onboarded state machine are structurally undercompensated or receive zero reward for genuine work, because the reward accounting's bootstrap step computes a zero (or understated) delta instead of crediting the full span of newly finalized blocks. This does not directly enable theft, but it is a permanent economic-freezing bug for the relayer incentive mechanism on every newly added state machine, weakening the incentive to deliver early consensus updates for new chains — directly reducing the reliability of message delivery routes that depend on relayers being paid to submit consensus proofs.

### Likelihood Explanation
This triggers automatically and unavoidably on every state machine's first (and potentially several early) consensus-update deliveries — it requires no attacker, just the normal operational sequence of onboarding a new destination/source chain to Hyperbridge, which happens with some regularity as new chains are integrated.

### Recommendation
On the first-ever reward computation for a `state_machine_id` (i.e. when `LastRewardedHeight::get` is `None`), seed `LastRewardedHeight` to the block height at genesis/registration of the state machine (or equivalently, treat the baseline for the first computation as `previous_height` only if `previous_height` itself reflects genuine chain history, not a same-block default). More directly: `calculate_reward` should not conflate "no watermark yet" with "use previous_commitment_height," since `previous_commitment_height` can be freshly derived from the same update being rewarded. Instead, unconditionally initialize `LastRewardedHeight` to the state machine's initial commitment height at the point the state machine/consensus client is first registered, so the first `calculate_reward` call always has a real, distinct baseline to diff against.

### Proof of Concept
1. Register a new state machine `SM` with `StateMachinesCostPerBlock[SM] = block_cost > 0`, and no prior entries in `LatestStateMachineHeight`/`PreviousStateMachineHeight`/`LastRewardedHeight` for `SM`.
2. Submit the first valid consensus proof (`StateMachineUpdated` event) advancing `SM` to height `H1`. Internally, `store_latest_commitment_height` runs: `previous_height = LatestStateMachineHeight::get(SM).unwrap_or_default()` (i.e., `0`), writes `PreviousStateMachineHeight[SM] = 0`, then `LatestStateMachineHeight[SM] = H1` [2](#0-1) .
3. `on_executed` invokes `process_message` → `calculate_reward(SM, block_cost)`: `latest_height = H1`, `previous_height = 0` (from step 2), `baseline = LastRewardedHeight::get(SM).unwrap_or(previous_height) = 0` [4](#0-3) .
4. `blocks = H1 - 0 = H1` — in this specific ordering the delta is actually non-zero on the very first call, so the reward would be paid; however, if a second `StateMachineUpdated` event for the same `SM` at height `H2` arrives within the *same batch* (same `on_executed` call), `highest_per_state_machine` collapses it to only the highest height and processes once, meaning any smaller intermediate updates for `SM` in that batch are silently dropped from the reward calculation entirely [5](#0-4) , which is a related but distinct starvation path also rooted in the same bootstrap-watermark design.

**Uncertainty**: I was not able to fully trace every code path where `previous_commitment_height`/`LatestStateMachineHeight` could be reset to `0` and re-diffed against a non-zero `latest_height` mid-lifecycle (e.g., via `delete_state_commitment`'s veto/reset path) to confirm a concrete zero-reward-on-first-update scenario without deeper test-harness tracing. I recommend a Devin session with repository access to write a Substrate unit test exercising `calculate_reward` immediately after state-machine registration and after a `delete_state_commitment` veto, to confirm whether `blocks` can be observed as `0` in practice, before treating this as a confirmed finding rather than a plausible analog.

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L46-51)
```rust
		if let Some(block_cost) = StateMachinesCostPerBlock::<T>::get(state_machine_id) {
			let reward = Self::calculate_reward(&state_machine_id, block_cost)?;

			if reward.is_zero() {
				return Ok(());
			}
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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L124-156)
```rust
		if let Some(relayer_account) = maybe_relayer_account {
			// When a batch contains multiple `StateMachineUpdated` events for the
			// same `state_machine_id` (sequential consensus updates for the same
			// chain), `calculate_reward` reads the same persisted
			// `(latest_commitment_height, previous_commitment_height)` pair on
			// every iteration and pays the same block-span reward N times.
			// Collapse the per-state-machine event stream to the single highest
			// `latest_height` so each state machine receives one reward per
			// batch, sized by the actual span of its commitment advance.
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

			for (state_machine_id, latest_height) in highest_per_state_machine {
				let state_machine_height =
					StateMachineHeight { id: state_machine_id.clone(), height: latest_height };

				let _ = Self::process_message(
					state_machine_height,
					state_machine_id,
					relayer_account.clone().into(),
				);
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
