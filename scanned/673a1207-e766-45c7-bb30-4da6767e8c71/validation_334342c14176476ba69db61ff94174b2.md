### Title
Double-application of a contract's pending storage diff to `ContractInfo` via `apply_pending_changes_to_contract` followed by `finalize_own_contributions`/`bank_pending_changes` - (File: `substrate/frame/revive/src/metering/storage.rs`)

### Summary
`RawMeter::apply_pending_changes_to_contract` mutates a live `ContractInfo` by applying the frame's pending `Diff` but deliberately does **not** reset `own_contribution`, so the same `Diff` remains staged in the meter. When the frame later finalizes via `finalize_own_contributions` or `bank_pending_changes`, the identical `Diff` is applied to `ContractInfo` a second time through `Contribution::update_contract`, double-counting the same storage delta.

### Finding Description
`apply_pending_changes_to_contract` is invoked before spawning a nested call frame so the child can observe the parent's not-yet-finalized storage bytes/items counts: [1](#0-0) 

Note it explicitly says it does **not** consume the pending diff ("Unlike `finalize_own_contributions`, this does not consume the pending diff, allowing the meter to continue tracking changes after the nested call returns"). It calls `diff.update_contract::<T>(Some(info))`, which mutates `info`'s stored byte/item deposit accounting fields in place, but leaves `self.own_contribution` as `Contribution::Alive(diff)` unchanged.

Later, when the same frame's meter is finalized, `finalize_own_contributions` re-applies that same unchanged `own_contribution` to `info` again: [2](#0-1) 

Or `bank_pending_changes` does the equivalent, applying the diff and only then resetting `own_contribution` to `Default`: [3](#0-2) 

Contrast this with `bank_pending_changes`, which explicitly resets `own_contribution = Contribution::Alive(Default::default())` right after applying the deposit — precisely to prevent double counting on a subsequent finalize. `apply_pending_changes_to_contract` has no equivalent reset, so if the same `ContractInfo` object that was mutated by `apply_pending_changes_to_contract` is the one later passed into `finalize_own_contributions`/`bank_pending_changes` for that same meter, the frame's `Diff` is applied to `info` twice — once early (to let the nested frame see updated totals) and once again at finalize time.

### Impact Explanation
If the diff is applied twice to the persisted `ContractInfo`, the contract's tracked `bytes`/`items` (and associated `bytes_deposit`/`items_deposit`) diverge from the actual child-trie state: a single storage write recorded once by the contract gets reflected twice in the deposit-relevant fields of `ContractInfo`. This can inflate or deflate the computed deposit depending on the sign of the diff (additions charge deposit, removals refund it), leading to either an over-refund (attacker gets storage deposit back it never paid a second time for) or persistent skew between charged deposit and actual on-chain storage usage — i.e., inconsistent deposit accounting across nested frames, matching the scoped "storage deposit underpayment / free storage growth" impact.

### Likelihood Explanation
This requires only an unprivileged contract that: (1) writes to its own storage, (2) makes a nested call (to itself or another contract) that triggers `new_nested_meter`/`apply_pending_changes_to_contract` on the same `ContractInfo`, and (3) returns normally so the parent frame reaches `finalize_own_contributions`/`bank_pending_changes` on the same `info`. This is a straightforward, repeatable contract call pattern reachable purely via `pallet_revive`'s call dispatch (extrinsic → contract → nested call), no privileged origin needed. However, I could not fully confirm from the retrieved code whether the `ContractInfo` instance mutated in `apply_pending_changes_to_contract` is guaranteed to be the exact same instance later passed to `finalize_own_contributions`/`bank_pending_changes` for that frame (the call sites in `substrate/frame/revive/src/exec.rs` that wire this together could not be fully retrieved in this session). If the caller reloads/discards the mutated `info` before the later finalize call (i.e., only a transient copy is affected), the double-application would not persist and the bug would not manifest.

### Recommendation
After `apply_pending_changes_to_contract` writes the diff into `info`, either (a) reset the tracked baseline so subsequent `update_contract` calls compute deltas relative to the already-applied state rather than re-applying the full diff, or (b) explicitly track "already applied to info" state (similar to what `bank_pending_changes` does with resetting `own_contribution`) so `finalize_own_contributions` does not redundantly reapply a diff that was already reflected in `info`.

### Proof of Concept
Rust unit test plan in `substrate/frame/revive/src/metering/storage/tests.rs`:
1. Build a `TestMeter` nested frame, `charge` it with a `Diff { bytes_added: X, items_added: Y, .. }`.
2. Call `apply_pending_changes_to_contract(&mut info)` and record `info.extra_deposit()`.
3. Call `finalize_own_contributions(Some(&mut info))` on the same meter/`info`.
4. Assert `info.extra_deposit()` after step 3 equals the deposit expected from applying the diff **once** (`Diff::update_contract` result computed independently), and fail the test if it instead reflects the diff applied twice (e.g., `bytes_deposit`/`items_deposit` doubled relative to a single independent `Diff` application on a fresh `ContractInfo`).

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L487-494)
```rust
	/// Determine the actual final charge from the own contributions
	pub fn finalize_own_contributions(&mut self, info: Option<&mut ContractInfo<T>>) {
		let deposit = self.own_contribution.update_contract(info);
		self.own_contribution = Contribution::Checked(deposit);

		// no need to recalculate max_charged here as the consumed amount cannot increase
		// when taking removed bytes/items into account
	}
```

**File:** substrate/frame/revive/src/metering/storage.rs (L496-510)
```rust
	/// Apply pending storage changes to a ContractInfo without finalizing the meter.
	///
	/// This is used before creating a nested frame to ensure the child frame can see
	/// the parent's pending storage changes when calculating refunds.
	///
	/// Unlike [`Self::finalize_own_contributions`], this does not consume the pending diff,
	/// allowing the meter to continue tracking changes after the nested call returns.
	pub fn apply_pending_changes_to_contract(&self, info: &mut ContractInfo<T>) {
		if let Contribution::Alive(diff) = &self.own_contribution {
			// Apply the diff to update the ContractInfo's storage deposit fields.
			// We don't care about the return value (the deposit amount) here,
			// we just want to update the ContractInfo so child frames can see it.
			let _ = diff.update_contract::<T>(Some(info));
		}
	}
```

**File:** substrate/frame/revive/src/metering/storage.rs (L512-528)
```rust
	/// Apply the pending diff to `info` and push its deposit as a final charge, then reset
	/// `own_contribution` so finalize does not apply it a second time.
	pub fn bank_pending_changes(&mut self, contract: T::AccountId, info: &mut ContractInfo<T>) {
		if let Contribution::Alive(_) = &self.own_contribution {
			let deposit = self.own_contribution.update_contract(Some(info));
			self.own_contribution = Contribution::Alive(Default::default());
			if !deposit.is_zero() {
				self.charge_deposit(contract, deposit);
			}
		} else {
			debug_assert!(
				false,
				"on-stack ancestor frames have not finalized yet, so own_contribution \
				 should be Alive when banked; qed",
			);
		}
	}
```
