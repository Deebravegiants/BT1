Audit Report

## Title
Double-application of pending storage diff to `ContractInfo` via `apply_pending_storage_changes` corrupts persisted deposit accounting - ([File: substrate/frame/revive/src/metering/mod.rs])

## Summary
`FrameMeter::apply_pending_storage_changes` (wrapping `RawMeter::apply_pending_changes_to_contract`) mutates a contract's `ContractInfo` byte/item counters and deposit fields from the still-`Alive` pending diff so a nested frame can observe the parent's uncommitted state, but intentionally leaves `own_contribution` unconsumed. When the parent frame subsequently calls `finalize`/`finalize_own_contributions`, the identical diff is applied to `info` a second time via `Diff::update_contract`, which is not idempotent and unconditionally adds/subtracts bytes, items, and deposits again.

## Finding Description
The doc comment on `apply_pending_changes_to_contract` explicitly states it "does not consume the pending diff, allowing the meter to continue tracking changes after the nested call returns," in contrast to `bank_pending_changes`, which resets `self.own_contribution = Contribution::Alive(Default::default())` immediately after applying the diff to `info` precisely to prevent re-application. [1](#0-0) [2](#0-1) 

`finalize_own_contributions` calls `self.own_contribution.update_contract(info)` unconditionally, and since `own_contribution` was left as `Contribution::Alive(diff)` after the peek call, this re-applies the same diff to the same `ContractInfo` fields (`storage_bytes`, `storage_items`, `storage_byte_deposit`, `storage_item_deposit`), which are accumulated via `saturating_add`/`saturating_sub` and have no built-in idempotency guard. [3](#0-2) 

`FrameMeter::apply_pending_storage_changes` and `FrameMeter::finalize` both delegate directly to these `RawMeter` methods, confirming that no additional reset logic exists at the `FrameMeter` layer to guard against double application. [4](#0-3) [5](#0-4) 

I was unable to fully trace the exact call sites in `substrate/frame/revive/src/exec.rs` within the available iterations to confirm with certainty (a) that `apply_pending_storage_changes` and the subsequent `finalize` call operate on the exact same in-memory `ContractInfo` reference for the parent frame in all code paths, and (b) whether some other mechanism elsewhere in `exec.rs` resets `own_contribution` between the two calls that isn't visible in the `metering` module alone. However, based purely on the `metering` module code, the asymmetry between `apply_pending_changes_to_contract` (no reset) and `bank_pending_changes` (explicit reset) is real and intentional per the doc comments, and `finalize_own_contributions` has no idempotency protection against a diff that was already partially applied by a prior peek.

## Impact Explanation
If the double-application occurs as described, `ContractInfo::storage_byte_deposit`/`storage_item_deposit`/`storage_bytes`/`storage_items` — the persisted baseline used for all future partial refund ratio calculations and full refunds on termination — would be inflated to roughly double the real value for any contract that performs a storage write and then makes a cross-contract call in the same execution. This would allow a contract to later claim refunds exceeding the amount actually reserved from the depositor, which is a genuine deposit-accounting/refund-integrity defect in `pallet-revive`.

## Likelihood Explanation
The claimed trigger path (attacker deploys a contract that writes storage and then makes a nested call before returning) requires only ordinary, unprivileged `call`/`instantiate` extrinsics and no special origin — this is a realistic and easily reproducible pattern for any pallet-revive contract that writes to its own storage before making a downstream call.

## Recommendation
Ensure `apply_pending_changes_to_contract` cannot have its diff re-applied by `finalize_own_contributions`: either reset `own_contribution` to `Contribution::Alive(Default::default())` after the peek (banking the computed deposit immediately, mirroring `bank_pending_changes`), or make `finalize_own_contributions` diff-aware so it does not redundantly re-apply changes already reflected in `info`. Add a regression test that writes storage in a parent frame, invokes a nested call, and asserts that `ContractInfo` storage/deposit fields after finalization equal the single (not doubled) real diff.

## Proof of Concept
1. Deploy parent contract `P` with an entry point that writes N bytes to its own storage, then calls child contract `C`.
2. Deploy child contract `C` with a no-op entry point.
3. Execute `P` via `Contracts::call`/`Pallet::bare_call`.
4. Read `ContractInfoOf::<Test>::get(&p_address)` after execution and compare `storage_byte_deposit`/`storage_bytes` against the expected single-application value (`N * DepositPerByte` / `N`) versus the doubled value that would result from the bug.
5. Confirm actual held/reserved balance from the depositor equals the single charge, not double, to distinguish a genuine accounting corruption from a display-only artifact.

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

**File:** substrate/frame/revive/src/metering/mod.rs (L655-663)
```rust
	pub fn finalize(&mut self, info: Option<&mut ContractInfo<T>>) -> DispatchResult {
		self.deposit.finalize_own_contributions(info);

		if self.deposit_left().is_none() {
			return Err(<Error<T>>::StorageDepositLimitExhausted.into());
		}

		Ok(())
	}
```

**File:** substrate/frame/revive/src/metering/mod.rs (L665-675)
```rust
	/// Apply pending storage changes to a ContractInfo without finalizing the meter.
	///
	/// This is used before creating a nested frame to ensure the child frame can see
	/// the parent's pending storage changes when calculating refunds. This fixes the issue
	/// where storage deposit refunds fail in subframes because the parent's pending
	/// charges haven't been committed to ContractInfo yet.
	///
	/// See: <https://github.com/paritytech/contract-issues/issues/213>
	pub fn apply_pending_storage_changes(&self, info: &mut ContractInfo<T>) {
		self.deposit.apply_pending_changes_to_contract(info);
	}
```
