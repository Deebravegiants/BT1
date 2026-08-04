### Title
Double-application of pending storage diff via `apply_pending_changes_to_contract` before `finalize_own_contributions`/`bank_pending_changes` corrupts `ContractInfo` deposit accounting - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
`apply_pending_changes_to_contract` mutates a contract's `ContractInfo` (storage bytes/items counters and their deposits) using the meter's pending `Diff`, but deliberately leaves `own_contribution` unchanged so a nested call can "see" the parent's pending state. Because `own_contribution` is not reset, the same `Diff` is later re-applied to the (already-mutated) `ContractInfo` by `finalize_own_contributions` (or re-derived by `bank_pending_changes`), double-counting the parent's storage change against a `ContractInfo` that may have since been further mutated by the nested child frame.

### Finding Description
`apply_pending_changes_to_contract` explicitly documents that, unlike `finalize_own_contributions`, it "does not consume the pending diff" [1](#0-0) . It calls `diff.update_contract::<T>(Some(info))`, which is *not* idempotent: it both computes a charge/refund pro-rata against the current `info.storage_bytes`/`info.storage_byte_deposit` and mutates those same fields in place [2](#0-1) .

Because `own_contribution` (`Contribution::Alive(diff)`) is left untouched after this call, any subsequent call on the same nested meter that also invokes `update_contract` on `own_contribution` - either `finalize_own_contributions` [3](#0-2)  or `bank_pending_changes` [4](#0-3)  - will re-apply the *same* `Diff` object to `info` a second time. Since a nested call intervenes between these two calls and may itself mutate the same `ContractInfo` (via its own `absorb`/`update_contract` calls on the child meter), the second application computes its charge/refund ratios against an `info` state that already reflects both the first (stale) application of the parent's diff and the child frame's unrelated changes. This mixes the parent's already-recorded diff with the child's newly-recorded storage changes when computing the pro-rata refund ratio in `Diff::update_contract`, and doubles the `bytes_added`/`items_added` charge and counter increments for the parent's own diff.

Concretely: a contract that writes to its own storage, then makes a nested call (invoking `new_nested`/entering a child frame) that reads/writes the same child-trie keys, then returns, causes the outer frame's `own_contribution` to be applied to `ContractInfo` twice - once via `apply_pending_changes_to_contract` before the nested call, and once via `finalize_own_contributions`/`bank_pending_changes` after it returns - with the child frame's own contribution to `info` sandwiched in between. This breaks the accounting invariant that a `Diff` is applied to `ContractInfo` exactly once.

### Impact Explanation
The double application corrupts `ContractInfo.storage_bytes`/`storage_items` and their associated deposits: the counters used as the denominator for future pro-rata refund calculations become permanently inflated or otherwise inconsistent with actual child-trie state. This directly violates the tested invariant ("storage deposit and weight accounting must stay consistent across nested frames") and can cause either the caller to be charged twice for the same bytes/items in the same call (overcharge) or, because future refunds are computed as `removed / info.storage_bytes`, cause future legitimate storage removals to be under-refunded once the counters are inflated - i.e., persistent state drift in `ContractInfo` deposit bookkeeping, matching the scoped "storage deposit underpayment / free storage growth" impact for subsequent transactions.

### Likelihood Explanation
This requires only an unprivileged contract call: any contract that writes to its own storage and then performs a nested call (to itself or another contract) touching the same `ContractInfo`/child trie triggers the code path where `apply_pending_changes_to_contract` is used ahead of a nested frame and the outer frame's `own_contribution` is finalized afterward. This is a standard, easily-reachable contract call pattern (self-recursive or reentrant call with prior storage writes), requiring no special privileges.

### Recommendation
Make `apply_pending_changes_to_contract` consume/reset the pending diff the same way `bank_pending_changes` does (i.e., apply the diff to `info`, then reset `own_contribution` to `Contribution::Alive(Default::default())` so subsequent writes start from a clean diff), or alternatively have callers snapshot and clear the diff before it becomes visible to nested frames, ensuring each recorded diff is applied to `ContractInfo` exactly once regardless of nested-call ordering.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/metering/storage/tests.rs` style:
1. Construct a `Nested` `RawMeter`, call `charge(&Diff { bytes_added: 100, .. })`.
2. Call `apply_pending_changes_to_contract(&mut info)` and record `info.storage_bytes`/`info.storage_byte_deposit`.
3. Simulate a nested frame's `absorb` call that adds its own unrelated bytes to the same `info`.
4. Call `finalize_own_contributions(Some(&mut info))` and assert that `info.storage_bytes`/`storage_byte_deposit` reflect only a single application of the original 100-byte diff (not double-counted along with the nested frame's contribution).
5. Assert failure: current code doubles the bytes_added contribution in `info`, proving the double-application bug.

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
