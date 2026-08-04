Based on the evidence gathered, I found a documented and already-fixed analog of this exact vulnerability class in `pallet-nomination-pools`.

### Title
Retroactive re-rating of accrued commission/rewards on `set_commission_max` (now fixed) - ([File: substrate/frame/nomination-pools/src/lib.rs])

### Summary
The Zaros report describes retroactive application of admin-changed accrual-rate parameters to already-accrued fees that had not yet been "settled." I searched for the analogous pattern in Polkadot SDK — an admin extrinsic that changes an accrual-rate parameter (commission) without first snapshotting/settling amounts already accrued at the old rate — and found that exactly this bug existed and was fixed in `pallet-nomination-pools`, documented in `prdoc/pr_12397.prdoc`.

### Finding Description
Per the changelog entry [1](#0-0) , `set_commission_max` would force-lower `commission.current` via `try_update_max` when the new maximum was below the currently active commission rate, but it did so *without first calling `update_records`* to snapshot/settle rewards accrued at the higher (pre-change) rate. As a result, rewards that had accrued since the last snapshot at the higher commission rate were re-rated at the new, lower commission rate the next time `update_records` ran — crediting the difference `(old_current - new_max) * accrued` to pool members instead of to the commission payee. This is structurally identical to the Zaros bug: an admin-controlled rate parameter is changed, and the change is applied retroactively to a period of unsettled accrual because the "settlement" step was not performed prior to the parameter update. The fix (already present in this codebase per the prdoc) mirrors the ordering used in `set_commission`, snapshotting the reward pool at the current commission rate before applying the cut.

For comparison, the general "accrue now, settle lazily on next interaction" pattern that enables this class of bug is a common design in FRAME (e.g., `pallet-transaction-payment`'s `NextFeeMultiplier` [2](#0-1) , and `staking-async`'s deferred/lazy slashing [3](#0-2) ), but in those cases the parameter changes are either forward-only (fee multiplier applies going forward, not retroactively to already-paid fees) or take effect only at the next era boundary by design (e.g. `set_max_commission` / `set_validator_self_stake_incentive_config` in `staking-async` explicitly document "changes take effect in the next era" [4](#0-3) ), so they do not retroactively re-rate an already-accrued-but-unsettled quantity.

### Impact Explanation
As documented, the underlying bug (before the fix landed) would have caused a real fund-transfer misallocation: commission that should have accrued to the pool's commission payee at the pre-change rate would instead be credited to pool members, i.e. a direct accounting/fund-safety defect analogous to the Zaros unfair funding-rate settlement. Since the fix is already present in the current codebase, there is no exploitable path in the current state of this repo for this specific case.

### Likelihood Explanation
Not applicable to the current codebase state — the fix (snapshot rewards via `update_records` before `try_update_max` lowers `commission.current`) has already been merged, per `prdoc/pr_12397.prdoc`. I was not able to fully re-verify the exact current implementation of `set_commission_max`/`try_update_max`/`update_records` line-by-line in `substrate/frame/nomination-pools/src/lib.rs` within the available search iterations (grep located the function names but I ran out of iterations to read the full bodies), so I cannot state with certainty whether the fix is complete or whether any residual edge case remains (e.g., other paths that mutate `commission.current` such as `set_commission` itself, or `set_commission_change_rate` interactions).

### Recommendation
Given the fix already exists, the recommendation is to verify (in a follow-up session with full file access) that:
1. All code paths that can lower `commission.current` (not just `set_commission_max`) call `update_records`/an equivalent snapshot **before** mutating the rate.
2. Add a regression test (if not already present) asserting that commission accrued before a `set_commission_max` call is credited to the commission payee rather than re-rated at the new maximum.

### Proof of Concept
I do not have a working, reproducible PoC against the current codebase, because the referenced fix in `prdoc/pr_12397.prdoc` indicates the vulnerable code path has already been patched, and I could not fully re-verify the current `set_commission_max`/`try_update_max` implementation within the available tool budget. Given the disqualification criteria (no reachable, currently-exploitable attacker path could be confirmed), this should be treated as **informational / already-remediated** rather than a new actionable finding.

### Citations

**File:** prdoc/pr_12397.prdoc (L1-12)
```text
title: 'nomination-pools: snapshot rewards before `set_commission_max` lowers current commission'
doc:
- audience: Runtime Dev
  description: |-
    `set_commission_max` force-lowers `commission.current` (via `try_update_max`) when the new max
    is below the active rate, but did not first call `update_records`. Rewards accrued at the higher
    rate since the last snapshot were therefore re-rated at the new lower rate on the next
    `update_records`, crediting the differential `(old_current - new_max) * accrued` to members
    instead of the commission payee.

    The fix snapshots the reward pool at the current commission before the cut, mirroring the
    ordering already used in `set_commission`.
```

**File:** substrate/frame/transaction-payment/src/lib.rs (L412-415)
```rust
	#[pallet::storage]
	#[pallet::whitelist_storage]
	pub type NextFeeMultiplier<T: Config> =
		StorageValue<_, Multiplier, ValueQuery, NextFeeMultiplierOnEmpty>;
```

**File:** substrate/frame/staking-async/src/lib.rs (L130-141)
```rust
//! ### Phase 4: Application
//!
//! Based on `SlashDeferDuration`, slashes are either:
//!
//! **Immediate (SlashDeferDuration = 0)**:
//! - Applied right away in the same block
//! - Funds deducted from staking ledger immediately
//!
//! **Deferred (SlashDeferDuration > 0)**:
//! - Stored in `UnappliedSlashes` for future application
//! - Applied at era: `offence_era + SlashDeferDuration`
//! - Can be cancelled by governance before application
```

**File:** substrate/frame/staking-async/src/pallet/mod.rs (L3143-3147)
```rust
		/// Configure the validator self-stake incentive parameters.
		///
		/// The dispatch origin must be `T::AdminOrigin`.
		///
		/// Changes take effect in the next era when rewards are calculated.
```
