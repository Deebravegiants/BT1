### Title
Double-application of the same storage `Diff` to `ContractInfo` inflates storage-deposit refunds - ([File: substrate/frame/revive/src/metering/storage.rs])

### Summary
`RawMeter::apply_pending_changes_to_contract` (invoked by `FrameMeter::apply_pending_storage_changes` in `substrate/frame/revive/src/metering/mod.rs:673-675`) mutates the real `ContractInfo` fields (`storage_bytes`, `storage_items`, `storage_byte_deposit`, `storage_item_deposit`) via `Diff::update_contract`, but never resets `own_contribution` afterwards. [1](#0-0)  Because the pending diff stays `Alive` and is not consumed, any later point in the same frame's lifetime that re-derives a deposit from that diff (another `apply_pending_storage_changes` call ahead of a further nested call, `bank_pending_changes`, or the final `finalize_own_contributions`) recomputes and re-mutates `ContractInfo` using the *entire accumulated* diff again on top of already-updated info — effectively applying the same byte/item delta more than once.

### Finding Description
`Diff::update_contract` is not idempotent: it both computes a `Deposit` and permanently mutates the passed `info` (`info.storage_bytes`, `info.storage_items`, `info.storage_byte_deposit`, `info.storage_item_deposit`), including refund ratios computed as `bytes_removed / info.storage_bytes` at call time. [2](#0-1) 

`apply_pending_changes_to_contract` was added to fix contract-issues#213 so that a *child* frame calling into the same contract can see the parent's not-yet-finalized diff. It calls `diff.update_contract::<T>(Some(info))` and discards the return value, but deliberately leaves `self.own_contribution` as `Contribution::Alive(diff)` unchanged so "the meter to continue tracking changes after the nested call returns." [1](#0-0) 

The problem is that `own_contribution` keeps accumulating the *entire* diff since the frame started (via `RawMeter::charge`, which does `own = own.saturating_add(diff)`), and it is only ever reset by `bank_pending_changes` (explicitly resets to `Contribution::Alive(Default::default())` after banking) or converted to `Checked` by `finalize_own_contributions`. [3](#0-2) [4](#0-3)  `apply_pending_changes_to_contract` is the odd one out: it mutates `info` but does not reset or checkpoint the diff.

Consequence: if a contract frame issues more than one nested call over its lifetime (e.g. a chain of delegate-calls A→B→A that each re-enter the same frame's storage), `apply_pending_storage_changes` gets invoked once per nested-call entry, each time re-applying the *full cumulative* diff (including bytes/items already committed to `info` by the previous invocation) on top of the already-mutated `ContractInfo`. Since `update_contract`'s refund ratio is computed from `info.storage_bytes`/`info.storage_items` *at call time*, and those fields were already reduced by the prior application, each repeated application both double-subtracts from `info.storage_byte_deposit`/`storage_item_deposit` and returns an additional non-zero `Deposit::Refund` that eventually gets banked (via `bank_pending_changes`, which pushes it into `self.charges` and thus into the final `E::charge` transfer at `execute_postponed_deposits`) or folded into the frame's final `finalize_own_contributions` result. The end effect is that the same underlying storage shrinkage is refunded to the caller more than once, and `info.storage_byte_deposit`/`storage_item_deposit` can be driven down (via repeated `saturating_sub`) further than the deposit that was actually charged for the remaining storage.

None of the existing checks catch this: `charge_contract_deposit_and_transfer` / `record_contract_storage_changes` only enforce the deposit *limit* (`adjust_effective_weight_limit`, `deposit_left().is_none()`), which caps how much can be *charged*, not how much can be *refunded*; there is no invariant anywhere checking that a diff is applied to `ContractInfo` at most once. [5](#0-4) 

### Impact Explanation
A contract that structures its execution as a sequence of nested calls into the same contract account (e.g. delegate-call chains that re-enter itself/peers sharing the same `ContractInfo`) can cause its own accumulated storage-shrinkage diff to be applied to `ContractInfo` more than once before it is finally banked. Each extra application yields an additional `Deposit::Refund` that is queued into `self.charges` and ultimately paid out via `E::charge`/`Pallet::refund_deposit` in `execute_postponed_deposits`, letting the caller reclaim more storage-deposit balance than was ever actually held for the deleted/shrunk storage — i.e., stealing funds via an inflated storage-deposit refund, matching the scoped impact.

### Likelihood Explanation
The precondition is simply that a single call frame performs storage writes/deletions and then issues **more than one** nested call in sequence (delegate-call or ordinary call into the same contract/account/context that shares the `ContractInfo`), which is entirely under an unprivileged contract author's control and requires no special origin, proxy, or admin privilege. This is a normal, permissionless contract-authoring pattern (self-delegatecall loops are common e.g. for proxy/upgradeable-contract patterns), making the bug straightforward to trigger repeatably and deterministically.

### Recommendation
Make `apply_pending_changes_to_contract` non-destructive to future diff calculations: instead of mutating `info` in place and leaving `own_contribution` untouched, either
1. checkpoint the diff already exposed to children (e.g. track an `applied_diff` baseline and only apply the *delta* since the last `apply_pending_storage_changes` call to `info`), or
2. compute a preview (non-mutating) projection of `info` for child visibility without mutating the authoritative `ContractInfo`, deferring all real mutation to `finalize_own_contributions`/`bank_pending_changes` exactly once per net diff.

In all cases, guarantee the invariant that any given accumulated `Diff` is applied to `ContractInfo`'s byte/item counters and deposit fields **exactly once** for its whole lifetime, regardless of how many times `apply_pending_storage_changes` is called before it is finally banked.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/metering/storage.rs` (or `tests.rs`) style:
```rust
// Pseudocode outline of the assertion to add to metering::storage::tests
#[test]
fn apply_pending_changes_does_not_double_refund() {
    let mut info = ContractInfo { storage_bytes: 1000, storage_byte_deposit: 1000, storage_items: 10, storage_item_deposit: 100, .. };
    let mut meter = RawMeter::<Test, Ext, Nested>::default();

    // simulate a large deletion recorded once
    meter.charge(&Diff { bytes_removed: 500, items_removed: 5, ..Default::default() });

    // first "nested call" boundary: exposes pending diff to a child
    meter.apply_pending_changes_to_contract(&mut info);
    let deposit_after_first = info.storage_byte_deposit;

    // second "nested call" boundary in the SAME frame (e.g. delegatecall loop)
    meter.apply_pending_changes_to_contract(&mut info);
    let deposit_after_second = info.storage_byte_deposit;

    // BUG: deposit is reduced again even though no new storage change occurred
    assert_eq!(deposit_after_first, deposit_after_second,
        "the same diff must not be re-applied to ContractInfo on a second call");
}
```
Expected (fixed) behavior: `deposit_after_first == deposit_after_second` because no additional storage change happened between the two calls. Currently, the second call further reduces `info.storage_byte_deposit`/`storage_item_deposit` (and would generate an extra `Deposit::Refund` if routed through `bank_pending_changes`), proving the cumulative diff is being re-applied and the refund is double-counted.

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

**File:** substrate/frame/revive/src/metering/storage.rs (L462-470)
```rust
	pub fn charge(&mut self, diff: &Diff) {
		match &mut self.own_contribution {
			Contribution::Alive(own) => {
				*own = own.saturating_add(diff);
				self.recalulculate_max_charged();
			},
			_ => panic!("Charge is never called after termination; qed"),
		};
	}
```

**File:** substrate/frame/revive/src/metering/storage.rs (L487-528)
```rust
	/// Determine the actual final charge from the own contributions
	pub fn finalize_own_contributions(&mut self, info: Option<&mut ContractInfo<T>>) {
		let deposit = self.own_contribution.update_contract(info);
		self.own_contribution = Contribution::Checked(deposit);

		// no need to recalculate max_charged here as the consumed amount cannot increase
		// when taking removed bytes/items into account
	}

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
