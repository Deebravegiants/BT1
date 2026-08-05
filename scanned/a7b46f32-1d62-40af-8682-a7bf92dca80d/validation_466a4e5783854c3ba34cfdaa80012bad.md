### Title
Reentrant same-contract calls cause `own_contribution` storage diff to be applied twice to `ContractInfo` - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
`RawMeter::apply_pending_changes_to_contract` (lines 503-510) mutates a contract's `ContractInfo` (`storage_bytes`/`storage_items`/`storage_byte_deposit`/`storage_item_deposit`) via `Diff::update_contract`, but deliberately leaves `own_contribution` in the `Alive` state instead of resetting it, per its own doc comment ("this does not consume the pending diff"). If the same frame later reaches normal completion, `finalize_own_contributions` (lines 488-494) calls `update_contract` again on the *same, still-`Alive`* diff against the (already mutated) `ContractInfo`, re-applying the identical byte/item delta a second time.

### Finding Description
`Diff::update_contract` (lines 121-173) is not idempotent: each invocation unconditionally adds `bytes_added`/`items_added` (net of removed) onto `info.storage_bytes`/`info.storage_items` and adjusts `storage_byte_deposit`/`storage_item_deposit` accordingly. Whether a call double-counts depends entirely on whether the diff being applied is cleared/consumed afterward.

Two sibling helpers exist with different semantics:
- `bank_pending_changes` (lines 514-528) applies the diff, then explicitly resets `self.own_contribution = Contribution::Alive(Default::default())` and books the resulting deposit as a `Charge`, so a later `finalize_own_contributions` call sees an empty diff and is a no-op for that portion.
- `apply_pending_changes_to_contract` (lines 503-510) applies the exact same kind of diff to `info` but takes `&self` and never touches `own_contribution`, leaving it `Alive` with the original (unconsumed) diff.

The doc comment for `apply_pending_changes_to_contract` explicitly states its purpose: expose a parent frame's pending storage changes to a nested (reentrant) child frame operating on the same contract account (`CALL`/`STATICCALL` with `AllowReentry`), so the child's refund-ratio calculation in `Diff::update_contract` uses up-to-date `info.storage_bytes`/`storage_items`. Because it does not consume the diff, if the parent frame subsequently finishes normally and its `finalize_own_contributions` runs against the same `own_contribution` (still holding the identical, already-applied `Diff::Alive`), the parent's byte/item delta gets folded into `info` a second time — inflating `storage_items`, `storage_bytes`, `storage_item_deposit`, and `storage_byte_deposit` beyond what the actual on-chain writes justify. Because `ContractInfo` is the persisted per-contract state used for all future deposit/refund pro-rata calculations (`Diff::update_contract`'s ratio computation depends on `info.storage_bytes`/`info.storage_items`), this inflation is not transient — it corrupts the baseline used for every subsequent transaction's refund math for that contract.

### Impact Explanation
An attacker-controlled contract that performs a same-contract reentrant call (`X` calls itself via `CALL`/`STATICCALL` with `AllowReentry`, writing storage in the parent frame before reentering, matching the "write→reenter→write" pattern referenced from PR #12267) can cause the persisted `ContractInfo.storage_items`/`storage_bytes`/`storage_item_deposit`/`storage_byte_deposit` fields to be inflated relative to the true storage footprint. This corrupts deposit accounting that persists in storage across transactions, leading to incorrect (generally under-refunded, since the base for future ratio calculations is inflated) refund/charge amounts on later storage operations for that contract — a bad-accounting bug in the deposit/charge and refund invariant that the metering system is supposed to preserve.

### Likelihood Explanation
This requires no privileged access: any unprivileged account can deploy or call a contract designed to reenter itself (a common, permitted pattern under `AllowReentry`) and perform a storage write in the parent frame prior to the reentrant sub-call, then let the outer call complete normally. The bug is deterministic and repeatable on every such write→reenter→(return) sequence, as long as `apply_pending_changes_to_contract` is invoked on that frame's own contract before/around the reentrant call and the frame's normal completion still routes through `finalize_own_contributions` on the un-reset `own_contribution`.

### Recommendation
`apply_pending_changes_to_contract` must not leave `own_contribution` in a state that will be independently re-applied later. Either: (a) have it record the applied portion and subtract it out of `own_contribution` (converting the diff into an "already-applied" baseline so subsequent `update_contract` calls compute deltas relative to what's already been persisted), or (b) route the reentrant-preview path exclusively through `bank_pending_changes` (which correctly resets `own_contribution` and books the charge), eliminating the separate non-consuming variant, or (c) make `finalize_own_contributions` aware that part of the diff was already committed via a "previewed" marker so it does not reapply it.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/metering/storage/tests.rs` style (extending existing `RawMeter` test harness):
1. Build a `ContractInfo` baseline (`storage_items = 0`, `storage_bytes = 0`, deposits = 0).
2. Create root meter, create nested meter for contract `X`.
3. Simulate a storage write in `X`'s frame: `nested.charge(&Diff { bytes_added: N, items_added: 1, .. })`.
4. Call `nested.apply_pending_changes_to_contract(&mut info)` to simulate exposing state to a reentrant `X→X` call (as would happen before entering the nested/reentrant sub-frame).
5. Simulate the reentrant sub-call doing nothing further, returning normally.
6. Call `nested.finalize_own_contributions(Some(&mut info))` to simulate the parent frame's normal completion.
7. Absorb into root meter and call `execute_postponed_deposits`.
8. Assert: `info.storage_items == 1` (not `2`), `info.storage_bytes == N` (not `2*N`), and `info.storage_item_deposit`/`storage_byte_deposit` equal the single-write baseline computed from a control run that never calls `apply_pending_changes_to_contract` (i.e., a non-reentrant `X` write only, using only `finalize_own_contributions`). The test should currently fail, showing `storage_items`/`storage_bytes`/deposits at double the expected baseline, proving the double-application. [1](#0-0) [2](#0-1)

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

**File:** substrate/frame/revive/src/metering/storage.rs (L487-529)
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
}
```
