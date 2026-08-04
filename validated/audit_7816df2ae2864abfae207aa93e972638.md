## Analysis

The sDai report's vulnerability class is: **a global state flag (`paused`) causes a hard revert on the withdrawal path, blocking users from retrieving even the funds/shares they are otherwise entitled to, with no fallback.**

Searching pallet-staking-async (which handles bonding/unbonding for the relay chain's staking system), I found a structurally analogous pattern in `do_withdraw_unbonded`.

### Title
Full revert of `withdraw_unbonded` due to unrelated unapplied slashes in the previous era - (File: `substrate/frame/staking-async/src/pallet/impls.rs`)

### Summary
`Pallet::do_withdraw_unbonded` unconditionally reverts the entire withdrawal extrinsic if *any* unapplied slash exists for the previous era, even when the calling account's own unlocking chunks are completely unrelated to that slash and have already matured past `BondingDuration`.

### Finding Description
`do_withdraw_unbonded` begins with a hard, all-or-nothing gate: [1](#0-0) 

which calls: [2](#0-1) 

`ensure_era_slashes_applied` checks `UnappliedSlashes::<T>::contains_prefix(era)` for the *entire previous era* — not scoped to the calling stash/validator. If any validator anywhere in the network has an unapplied slash pending from the previous era, the `ensure!` reverts the whole call with `Error::UnappliedSlashesInPreviousEra`, before any of the caller's own unlocking chunks are inspected via `calculate_earliest_withdrawal_era` / `consolidate_unlocked`.

This mirrors the sDaiStrategy pattern: a chain-wide condition (`paused` in sDai; "unapplied slash exists somewhere" here) causes a full revert of the withdrawal path rather than allowing the unaffected portion of funds to be released.

This is confirmed by the test `withdrawals_are_blocked_for_unprocessed_and_unapplied_slashes`, which shows a nominator's `withdraw_unbonded` call reverting with `UnappliedSlashesInPreviousEra` purely because *other validators* had unapplied slashes pending, unrelated to the nominator's own unbonding chunks: [3](#0-2) 

Notably, this behavior is intentional and documented — it is a defensive measure introduced in [4](#0-3) , explicitly to preserve slashing guarantees, and the docs state it is "extremely rare" and expected to be transient (resolved once `apply_slash` — a **permissionless** call — is executed): [5](#0-4) 

### Impact Explanation
Unlike sDaiStrategy (where pausing withdrawals is a pure design flaw with no recovery path other than admin unpausing), this pallet's block is recoverable by *any* account calling the permissionless `apply_slash`, and it is scoped to a single era window rather than indefinite. The practical impact is a temporary DoS on `withdraw_unbonded` for all stakers network-wide whenever slash processing lags by one era — not a fund-loss or permanent-lock issue.

### Likelihood Explanation
Low-to-rare in practice: it requires validator misbehavior producing more offences in an era than can be processed/applied within the following era (a throughput/spam scenario), which the pallet's own documentation and tests characterize as an edge case ("extremely unlikely... likely indicates offence spam").

### Recommendation
Since this is a known, deliberate, and documented trade-off (with an already-provided permissionless recovery mechanism via `apply_slash`), it does not represent an accidental bug analogous to the sDai finding. If tighter behavior is desired, the check could be scoped to only the specific stash/validator being withdrawn from, rather than any validator network-wide, to reduce the blast radius of the temporary block.

### Proof of Concept
See `withdrawals_are_blocked_for_unprocessed_and_unapplied_slashes` in [6](#0-5)  — it reproduces the exact scenario: an uninvolved nominator's `withdraw_unbonded` call reverts due to unrelated validators' unapplied slashes in the previous era.

**Caveat:** This is the closest structural analog found for the "pause blocks all withdrawals" vulnerability class in this codebase. It differs materially from the sDai report in that it is an intentionally documented defensive measure with a permissionless self-healing recovery path, not an oversight — so I would not classify it with the same severity as the original finding.

### Citations

**File:** substrate/frame/staking-async/src/pallet/impls.rs (L259-267)
```rust
	pub(super) fn do_withdraw_unbonded(controller: &T::AccountId) -> Result<Weight, DispatchError> {
		let mut ledger = Self::ledger(Controller(controller.clone()))?;
		let (stash, old_total) = (ledger.stash.clone(), ledger.total);
		let active_era = Rotator::<T>::active_era();

		// Ensure last era slashes are applied. Else we block the withdrawals.
		if active_era > 1 {
			Self::ensure_era_slashes_applied(active_era.saturating_sub(1))?;
		}
```

**File:** substrate/frame/staking-async/src/pallet/impls.rs (L319-325)
```rust
	fn ensure_era_slashes_applied(era: EraIndex) -> Result<(), DispatchError> {
		ensure!(
			!UnappliedSlashes::<T>::contains_prefix(era),
			Error::<T>::UnappliedSlashesInPreviousEra
		);
		Ok(())
	}
```

**File:** substrate/frame/staking-async/src/tests/slashing.rs (L1569-1651)
```rust
#[test]
fn withdrawals_are_blocked_for_unprocessed_and_unapplied_slashes() {
	ExtBuilder::default()
		.slash_defer_duration(2)
		.bonding_duration(3)
		.add_staker(61, 1000, StakerStatus::Validator)
		.add_staker(71, 1000, StakerStatus::Validator)
		.add_staker(81, 1000, StakerStatus::Validator)
		.add_staker(91, 1000, StakerStatus::Validator)
		// we want to replicate a scenario where all offences could not be processed in 1 era, so we
		// reduce the era length to 1 block.
		.session_per_era(1)
		.period(1)
		.validator_count(6)
		.build_and_execute(|| {
			// NOTE for curious reader: Era change still takes 2 blocks... don't ask why ¯\_(ツ)_/¯
			let _expected_era_length = 2;

			// Set up nominator.
			let validator = 11;
			let nominator = 301;
			bond_nominator(nominator, 500, vec![validator]);

			// create unbonding chunks for the next two eras.
			Session::roll_until_active_era(2);
			assert_ok!(Staking::unbond(RuntimeOrigin::signed(nominator), 100));
			Session::roll_until_active_era(3);
			assert_ok!(Staking::unbond(RuntimeOrigin::signed(nominator), 150));

			// Rationale: We want to simulate a backlog of offences from era 3 that remain
			// unprocessed by the time unbonding becomes possible in era 6.
			//
			// Offences for era 3 must be reported no later than era 4, since slashing application
			// starts in era 5. To achieve this, we flood era 3 with more than 4 offences, all
			// reported just before the end of era 4. Given there are only 2 blocks per era
			// (limiting processing throughput), this ensures not all offences will be processed by
			// era 6 — blocking withdrawal as intended.

			// go to era 4.
			Session::roll_until_active_era(4);

			// roll one block of 2 of era 4.
			Session::roll_next();

			// flood offence pipeline with offences for era 3.
			// Note: our validator 11 is not slashed.
			add_slash_in_era(21, 3, Perbill::from_percent(10));
			add_slash_in_era(61, 3, Perbill::from_percent(10));
			add_slash_in_era(71, 3, Perbill::from_percent(10));
			add_slash_in_era(81, 3, Perbill::from_percent(10));
			add_slash_in_era(91, 3, Perbill::from_percent(10));

			// lets roll to era 6 where all unbonding chunks are available to withdraw.
			Session::roll_until_active_era(6);
			assert_eq!(active_era(), 6);

			// Ensure unbonding chunks can all be withdrawn by era 6.
			let expected_chunks: BoundedVec<UnlockChunk<Balance>, MaxUnlockingChunks> = bounded_vec![
				// era is unbond_era + bonding_duration, starting from era 2 + 3.
				UnlockChunk { era: 5, value: 100 },
				UnlockChunk { era: 6, value: 150 },
			];
			assert_eq!(Ledger::<T>::get(nominator).unwrap().unlocking, expected_chunks);

			// and we created 5 offences, of which 3 would be processed in last block of era 4, and
			// 2 blocks of era 5.
			assert_eq!(era_unprocessed_offence_count(3), 5 - 3);
			assert_eq!(OffenceQueueEras::<T>::get().unwrap(), vec![3]);

			// all nominator balance other than ED is staked.
			let nominator_balance_pre_withdraw = Balances::free_balance(&nominator);
			assert_eq!(nominator_balance_pre_withdraw, 1);

			// Since the eras are too short, the offences that needed to be applied for last era 5
			// are still unapplied. This will block the withdrawal.
			assert_eq!(era_unapplied_slash_count(5), 1);

			// WHEN: the nominator tries to withdraw unbonded funds while there are unapplied
			// offence in the last era.
			assert_noop!(
				Staking::withdraw_unbonded(RuntimeOrigin::signed(nominator), 0),
				Error::<T>::UnappliedSlashesInPreviousEra
			);
```

**File:** prdoc/stable2509/pr_9079.prdoc (L1-26)
```text
title: "Prevent withdrawals while processing offences"

doc:
  - audience: Runtime Dev
    description: |
      Adds withdrawal restrictions to prevent users from withdrawing unbonded funds while 
      there are unprocessed offences that could result in slashing. This is a defensive 
      measure that ensures slashing guarantees are maintained even in extreme edge cases.
      
      Key changes:
      - Withdrawals are blocked if there are unapplied slashes from the previous era 
        (returns `UnappliedSlashesInPreviousEra` error). This occurs when all unapplied 
        slashes for an era could not be applied within one era worth of blocks. While 
        one era is reserved for applying slashes page by page, if the era rolls over 
        before completion, these slashes can only be applied via the permissionless 
        `apply_slash` call.
      - Withdrawals are restricted to the minimum of the active era and the last fully 
        processed offence era
      - Unbonding chunks are now keyed by active era instead of current era
      - Offences arriving after their intended application era are rejected and emit 
        `OffenceTooOld` event
      
      Both the `UnappliedSlashesInPreviousEra` error and withdrawal restrictions due to 
      delayed offence processing are extremely rare scenarios that should not occur under 
      normal operation. These are defensive measures to handle edge cases where slash 
      processing is delayed beyond expected timelines.
```

**File:** substrate/frame/staking-async/src/lib.rs (L192-197)
```rust
//! ```
//!
//! **Key Restrictions**:
//! 1. Cannot withdraw if previous era has unapplied slashes
//! 2. Cannot withdraw funds from eras with unprocessed offences

```
