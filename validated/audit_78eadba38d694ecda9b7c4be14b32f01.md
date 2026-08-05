Audit Report

## Title
Double-application of pending storage diff in nested contract calls inflates/corrupts storage-deposit refund - (File: substrate/frame/revive/src/metering/storage.rs)

## Summary
`RawMeter::apply_pending_changes_to_contract` mutates `ContractInfo` using the frame's pending `own_contribution` diff but leaves `own_contribution` untouched afterward, unlike its sibling `bank_pending_changes`, which explicitly resets it to `Contribution::Alive(Default::default())` after application. When the same frame is subsequently finalized via `FrameMeter::finalize` → `finalize_own_contributions`, the identical, still-`Alive` diff is applied a second time to `ContractInfo` through `Contribution::update_contract`, corrupting the contract's storage byte/item counters and producing an inconsistent deposit refund/charge.

## Finding Description
`apply_pending_changes_to_contract` reads the diff and calls `diff.update_contract::<T>(Some(info))` purely to make pending changes visible to nested frames, but does not reset `own_contribution`: [1](#0-0) 

Compare this with `bank_pending_changes`, which performs the identical `update_contract` call but explicitly resets `own_contribution` to a fresh `Contribution::Alive(Default::default())` immediately afterward, specifically to prevent later re-application: [2](#0-1) 

`FrameMeter::apply_pending_storage_changes` exposes the unguarded method, and is documented as being called "before creating a nested frame ... so the child frame can see the parent's pending storage changes": [3](#0-2) 

Later, when the same frame is torn down normally, `FrameMeter::finalize` unconditionally calls `finalize_own_contributions`, which applies `self.own_contribution.update_contract(info)` again if `own_contribution` is still `Alive`: [4](#0-3) [5](#0-4) 

`Diff::update_contract` is not idempotent: it both mutates `info.storage_bytes`/`storage_items`/`storage_byte_deposit`/`storage_item_deposit` and computes refund ratios based on the *current* value of those fields at call time: [6](#0-5) 

Because the first call (via `apply_pending_storage_changes`) already advances `info`'s counters and deposit fields, a second call with the same `diff` (via `finalize`) computes its refund ratio against an already-advanced baseline and mutates the counters/deposits a second time — this is a genuine double-application, not a no-op. No guard, flag, or debug assertion exists on `RawMeter`/`ResourceMeter` to detect or prevent finalizing a frame whose pending diff was already partially materialized to `ContractInfo`.

## Impact Explanation
Since `ContractInfo`'s storage byte/item counters and deposit fields are advanced twice for a single logical storage diff, any frame that both writes storage and triggers a nested call (which is common — e.g., a contract that writes storage before calling out to another contract) will have its `ContractInfo` and resulting deposit refund/charge diverge from `per_byte * net_bytes_freed`. This directly corrupts the on-chain storage-deposit accounting used to reserve/refund balance for a contract's storage rent, which is an in-scope storage-deposit accounting/fund-safety issue for pallet-revive.

## Likelihood Explanation
The bug is reachable by any unprivileged account able to deploy contracts and issue a normal extrinsic invoking a contract that performs storage writes followed by a nested call (`seal_call`) before returning — no special privileges, governance, or other actors are required. This is a common contract pattern (write-then-call), and the asymmetry between `apply_pending_changes_to_contract` (no reset) and `bank_pending_changes` (explicit reset) is a straightforward, deterministic code path, not a contrived corner case, making it highly repeatable.

## Recommendation
Make `apply_pending_changes_to_contract` consume/reset the pending diff the same way `bank_pending_changes` does (reset `own_contribution` to `Contribution::Alive(Default::default())` after materializing it to `info`), or otherwise track that the diff has already been applied to `info` so that `finalize_own_contributions` does not reapply it. Add a debug assertion analogous to the one in `bank_pending_changes` to catch any frame teardown path that finalizes after `apply_pending_storage_changes` without proper reconciliation.

## Proof of Concept
1. Deploy a contract A that, within a single call, writes N bytes to its own storage via `seal_set_storage`, then performs a nested `seal_call` (e.g., into itself or contract B) before returning.
2. Trace the meter calls for A's frame: `apply_pending_storage_changes` is invoked before the nested dispatch (per `exec.rs`), mutating `ContractInfo` and leaving `own_contribution` as `Contribution::Alive(diff)`.
3. After the nested call returns, A's frame is torn down normally via `FrameMeter::finalize`, invoking `finalize_own_contributions`, which calls `update_contract` again with the same `diff` against the already-mutated `ContractInfo`.
4. Assert that the resulting `ContractInfo.storage_bytes`/`storage_byte_deposit` and the total deposit charged/refunded do not equal `DepositPerByte::get() * net_bytes_written`, demonstrating the double-application. This can be implemented as a unit test in `substrate/frame/revive/src/metering/storage.rs`'s test module, directly constructing a `RawMeter`, calling `charge`, then `apply_pending_changes_to_contract`, then `finalize_own_contributions`, and comparing `ContractInfo` state/deposit against a single-application baseline.

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L121-173)
```rust
	pub fn update_contract<T: Config>(&self, info: Option<&mut ContractInfo<T>>) -> DepositOf<T> {
		let per_byte = T::DepositPerByte::get();
		let per_item = T::DepositPerChildTrieItem::get();
		let bytes_added = self.bytes_added.saturating_sub(self.bytes_removed);
		let items_added = self.items_added.saturating_sub(self.items_removed);
		let mut bytes_deposit = Deposit::Charge(per_byte.saturating_mul((bytes_added).into()));
		let mut items_deposit = Deposit::Charge(per_item.saturating_mul((items_added).into()));

		// Without any contract info we can only calculate diffs which add storage
		let info = if let Some(info) = info {
			info
		} else {
			return bytes_deposit.saturating_add(&items_deposit);
		};

		// Refunds are calculated pro rata based on the accumulated storage within the contract
		let bytes_removed = self.bytes_removed.saturating_sub(self.bytes_added);
		let items_removed = self.items_removed.saturating_sub(self.items_added);
		let ratio = FixedU128::checked_from_rational(bytes_removed, info.storage_bytes)
			.unwrap_or_default()
			.min(FixedU128::from_u32(1));
		bytes_deposit = bytes_deposit
			.saturating_add(&Deposit::Refund(ratio.saturating_mul_int(info.storage_byte_deposit)));
		let ratio = FixedU128::checked_from_rational(items_removed, info.storage_items)
			.unwrap_or_default()
			.min(FixedU128::from_u32(1));
		items_deposit = items_deposit
			.saturating_add(&Deposit::Refund(ratio.saturating_mul_int(info.storage_item_deposit)));

		// We need to update the contract info structure with the new deposits
		info.storage_bytes =
			info.storage_bytes.saturating_add(bytes_added).saturating_sub(bytes_removed);
		info.storage_items =
			info.storage_items.saturating_add(items_added).saturating_sub(items_removed);
		match &bytes_deposit {
			Deposit::Charge(amount) => {
				info.storage_byte_deposit = info.storage_byte_deposit.saturating_add(*amount)
			},
			Deposit::Refund(amount) => {
				info.storage_byte_deposit = info.storage_byte_deposit.saturating_sub(*amount)
			},
		}
		match &items_deposit {
			Deposit::Charge(amount) => {
				info.storage_item_deposit = info.storage_item_deposit.saturating_add(*amount)
			},
			Deposit::Refund(amount) => {
				info.storage_item_deposit = info.storage_item_deposit.saturating_sub(*amount)
			},
		}

		bytes_deposit.saturating_add(&items_deposit)
	}
```

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
