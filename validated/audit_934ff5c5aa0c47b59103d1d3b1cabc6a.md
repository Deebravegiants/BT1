### Title
Double-application of a frame's pending storage diff to `ContractInfo` via `apply_pending_storage_changes` allows deposit-refund accounting to diverge from actual charged/reserved balance - ([File: substrate/frame/revive/src/metering/mod.rs])

### Summary
`FrameMeter::apply_pending_storage_changes` mutates a contract's live `ContractInfo` (byte/item counters and deposit fields) with the frame's *uncommitted* `own_contribution` diff so that a nested child frame can "see" the parent's pending storage changes when it computes its own refund. Unlike `bank_pending_changes`, this function deliberately does **not** reset `own_contribution` after mutating `info`, so the identical diff is applied to `info` a second time later when the parent frame calls `finalize_own_contributions`. This produces a double-application of the parent's pending charge/refund onto the persisted `ContractInfo`, which a nested callee can exploit by deleting overlapping keys while the parent's charge is only a "preview," not an actually-reserved deposit.

### Finding Description
`ResourceMeter::new_nested`/execution flow calls `FrameMeter::apply_pending_storage_changes`, which forwards to `RawMeter::apply_pending_changes_to_contract`: [1](#0-0) 

That function applies the frame's `own_contribution` `Diff` to the passed `info` for visibility purposes only, explicitly *without* resetting `own_contribution`: [2](#0-1) 

This is different from the sibling function `bank_pending_changes`, which performs the same mutation but *does* reset `own_contribution` to `Contribution::Alive(Default::default())` afterward specifically to avoid double counting: [3](#0-2) 

Because `apply_pending_changes_to_contract` leaves `own_contribution` untouched, the same diff is applied a second time when the frame eventually finalizes via `finalize_own_contributions`, which again calls `Contribution::update_contract(info)` on the (now already-mutated) `info`: [4](#0-3) 

`Diff::update_contract` is not idempotent — its refund ratio calculation is `removed_bytes / info.storage_bytes` (and analogous for items), and it mutates `info.storage_bytes`, `info.storage_items`, `info.storage_byte_deposit`, `info.storage_item_deposit` as a side effect: [5](#0-4) 

The exploit path the question describes follows directly from the purpose stated in the code comment — "This is used before creating a nested frame to ensure the child frame can see the parent's pending storage changes when calculating refunds" (referencing paritytech/contract-issues#213): [1](#0-0) 

1. Caller contract writes storage (accumulated only as an uncommitted `Diff` in its `FrameMeter.own_contribution`; nothing charged to origin yet).
2. Before instantiating/calling the callee, the caller's frame calls `apply_pending_storage_changes`, which pushes the pending write's byte/item counts and deposit amounts into the live `ContractInfo` — even though no balance has actually been reserved from the origin (`E::charge`/`ReservingExt::charge` only runs later, at `execute_postponed_deposits`, and even then only for `Charge`s already coalesced into `RawMeter::charges`, not for still-pending `own_contribution`).
3. The callee (child frame) deletes overlapping storage keys. Its own `Diff::update_contract` refund ratio is computed against the now-inflated `info.storage_bytes`/`info.storage_byte_deposit` (containing the parent's not-yet-real charge), so the child's refund is computed pro-rata against phantom deposit that was never actually reserved.
4. When the parent frame eventually finalizes (`FrameMeter::finalize` → `finalize_own_contributions`), the *same* pending diff is applied to `info` a second time, further corrupting the persisted per-contract byte/item/deposit counters.
5. `TransactionMeter::execute_postponed_deposits` then performs real balance transfers (`ReservingExt::charge` → `Pallet::refund_deposit`/`charge_deposit`) based on the `charges` vector, which was populated using these corrupted numbers, so total refunds paid out no longer necessarily equal the total legitimate net storage delta for the whole call stack.

No existing check catches this: `charge_deposit`/`record_charge` only enforce a deposit *limit*, not that the accounting is internally consistent, and there is no de-duplication guard preventing `apply_pending_changes_to_contract`'s mutation from being replayed by `finalize_own_contributions`.

### Impact Explanation
An unprivileged contract deployer can, through ordinary `instantiate`/`call` extrinsics, construct nested frames so that a child frame's refund is computed against a parent's uncommitted, not-actually-reserved storage deposit. This can cause the effective refund paid by `execute_postponed_deposits` to diverge from the true net storage delta of the call stack, letting the attacker reduce their legitimate storage deposit charge or obtain a refund not backed by an actual reserve — i.e., reserved balance is not correctly re-derived from real on-chain storage state.

### Likelihood Explanation
The precondition set is fully attacker-controlled and requires only standard, permissionless contract deployment: a caller contract that writes storage, and a callee contract instantiated from within the same call stack that deletes overlapping keys. No privileged origin, governance, or race condition is needed — the bug is a deterministic accounting-order issue triggered by ordinary nested contract calls, making it repeatable on every execution of the crafted contract pair.

### Recommendation
Make `apply_pending_changes_to_contract` consistent with `bank_pending_changes`: either (a) reset `own_contribution` to `Contribution::Alive(Default::default())` after applying it to `info` (mirroring `bank_pending_changes`), and adjust `finalize_own_contributions` bookkeeping accordingly so the final charge for the frame is still correctly summed, or (b) track a separate "already previewed" diff baseline so `finalize_own_contributions` computes only the delta beyond what was already applied to `info`, preventing any double application of the same byte/item/deposit changes to the persisted `ContractInfo`.

### Proof of Concept
Rust integration test in `substrate/frame/revive` pallet tests:
1. Deploy `Caller` contract that, on `call`, writes a storage key of `N` bytes (charge some deposit `D1`), then instantiates `Callee` passing a `deposit_limit` sized to reclaim `D1`.
2. `Callee` on `instantiate` deletes the same-sized storage key range from `Caller`'s child trie (via a crafted key collision or via a shared storage item that both frames operate on, if permitted by the contract model) or, more precisely, deletes its own storage sized to match `Caller`'s pending write so the refund ratio interacts with the same `ContractInfo`.
3. Assert `Currency::free_balance(origin)` before and after the whole transaction, and assert `total_consumed_deposit` returned by `execute_postponed_deposits` equals the true net delta: `(bytes_added - bytes_removed) * DepositPerByte + (items_added - items_removed) * DepositPerItem` computed independently from `ContractInfo`'s final state.
4. Expect the test to fail (deposit refunded/charged does not match expected net delta) if the double-application bug is present, proving the divergence.

### Citations

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
