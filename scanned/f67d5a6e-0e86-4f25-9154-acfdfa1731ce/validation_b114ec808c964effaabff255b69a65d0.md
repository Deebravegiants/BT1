### Title
Storage-metering asymmetry between `apply_pending_changes_to_contract` (non-consuming preview) and `bank_pending_changes` (consuming, resets diff) allows a pending `Diff` to be applied to `ContractInfo` twice - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
`RawMeter::apply_pending_changes_to_contract` mutates a contract's `ContractInfo` storage-accounting fields (`storage_bytes`, `storage_items`, `storage_byte_deposit`, `storage_item_deposit`) from the frame's still-`Alive` `own_contribution` diff, but deliberately does **not** reset `own_contribution`, unlike its sibling `bank_pending_changes`, which performs the identical mutation and then resets the diff to prevent re-application. If the same frame's `own_contribution` is later finalized normally (`finalize_own_contributions`/`FrameMeter::finalize`, invoked at the end of the frame's own execution or when absorbed by a caller), the identical `Diff` is applied to the same `ContractInfo` a second time.

### Finding Description
`apply_pending_changes_to_contract` at [1](#0-0)  calls `diff.update_contract::<T>(Some(info))` and explicitly discards the returned deposit amount ("we don't care about the return value"), while leaving `self.own_contribution` untouched (still `Contribution::Alive(diff)`). Crucially, `Diff::update_contract` is not idempotent: it directly mutates `info.storage_bytes`/`storage_items` by adding `bytes_added`/`items_added` computed straight from the `Diff`, and mutates `info.storage_byte_deposit`/`storage_item_deposit` accordingly, and further computes refund ratios using `info.storage_bytes`/`storage_items` as the denominator ( [2](#0-1) ).

By contrast, `bank_pending_changes` performs the same `update_contract` call but then explicitly resets `self.own_contribution = Contribution::Alive(Default::default())` specifically "so finalize does not apply it a second time" ( [3](#0-2) ) - a comment that itself documents developer awareness of exactly this double-application hazard.

Both are exposed via `FrameMeter::apply_pending_storage_changes` and `FrameMeter::bank_pending_storage_changes` ( [4](#0-3) ), added as the fix for `contract-issues#213` so that a child frame can see a parent's pending pro-rata refund ratio during reentrant/self-referential calls. If a frame that has called `apply_pending_storage_changes` (preview path, non-consuming) subsequently proceeds through the normal completion path — `FrameMeter::finalize` → `finalize_own_contributions` ( [5](#0-4) ) — the unchanged `Diff` is applied to the same `ContractInfo` a second time: `storage_bytes`/`storage_items`/`storage_byte_deposit`/`storage_item_deposit` are incremented again for bytes/items that were already accounted for in the preview call, and any subsequent refund-ratio computation for removed bytes/items uses this now-inflated denominator, permanently skewing future pro-rata refunds for the contract.

No check in `RawMeter`/`Contribution` guards against calling `update_contract` twice on an `Alive` diff without an intervening reset — the type system does not distinguish a "previewed" `Alive` diff from a fresh one, and the only reset mechanism (`bank_pending_changes`) is a separate, easily-diverging call path from the preview call (`apply_pending_changes_to_contract`).

### Impact Explanation
`ContractInfo`'s persisted storage accounting fields (`storage_bytes`, `storage_items`, `storage_byte_deposit`, `storage_item_deposit`) can be corrupted to values exceeding the real net storage diff and the real amount actually held from the origin account. This causes a permanent divergence between the contract's recorded deposit bookkeeping and its true state, degrading future refund correctness (since refunds are pro-rata against these fields) — a persistent storage-deposit accounting inconsistency as scoped by the question.

### Likelihood Explanation
Preconditions require a contract call pattern that exercises the preview path (`apply_pending_storage_changes`, added for contract-issues#213 to fix reentrant refund visibility) followed by the ordinary (non-banked) frame-finalization path (`finalize`/`absorb`) on the same frame without an intervening `bank_pending_storage_changes` reset. This is reachable by any unprivileged EVM-compatible contract caller through `pallet-revive` `eth_call`/`call`, since it only requires deploying a contract that performs a reentrant or cross-contract call-back touching the same storage key before its own frame finalizes — no privileged origin is needed. I was not able to inspect the exact call sites in `substrate/frame/revive/src/exec.rs` (grep found 7 usages) within the available tool budget to confirm whether existing call-site discipline in all current reentrancy code paths always pairs `apply_pending_storage_changes` with `bank_pending_storage_changes` rather than the ordinary `finalize`, so I cannot certify with full confidence that a concretely reachable double-application currently occurs on `main`; this should be verified with a targeted integration test.

### Recommendation
Make `apply_pending_changes_to_contract` consistent with `bank_pending_changes`: either (a) have it also reset/mark the diff as consumed and require the frame to re-derive incremental diffs for any further storage operations after the preview, or (b) make `Diff::update_contract` idempotent for a given frame lifecycle by tracking an "applied to info" flag on `Contribution::Alive` so a second `update_contract` call with the same diff is a no-op / debug_assert failure, mirroring the `debug_assert!` already present in `bank_pending_changes`. Additionally, audit every call site of `apply_pending_storage_changes` in `substrate/frame/revive/src/exec.rs` to guarantee it is always followed by `bank_pending_storage_changes` (never by the plain `finalize`) for that same frame/`ContractInfo` pair.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/metering/storage.rs::tests` (or an integration test under `substrate/frame/revive/src/tests.rs`):
1. Construct a `ContractInfo` with baseline `storage_bytes = 0`, `storage_byte_deposit = 0`.
2. Create a `Nested` `RawMeter`, call `charge(&Diff { bytes_added: 100, ..Default::default() })`.
3. Call `apply_pending_changes_to_contract(&mut info)` (simulating the pre-nested-call preview) and assert `info.storage_bytes == 100`.
4. Call `finalize_own_contributions(Some(&mut info))` (simulating normal frame completion without banking) and assert the returned/charged deposit and `info.storage_bytes`.
5. Expected (buggy) result: `info.storage_bytes == 200` and `info.storage_byte_deposit` reflects two charges of `per_byte * 100` instead of one — violating the invariant that total deposit/byte accounting for a single 100-byte write equals exactly one charge of `per_byte * 100` and `storage_bytes == 100`.

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

**File:** substrate/frame/revive/src/metering/storage.rs (L503-510)
```rust
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

**File:** substrate/frame/revive/src/metering/mod.rs (L665-685)
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

	/// See [`storage::RawMeter::bank_pending_changes`].
	pub fn bank_pending_storage_changes(
		&mut self,
		contract: T::AccountId,
		info: &mut ContractInfo<T>,
	) {
		self.deposit.bank_pending_changes(contract, info);
	}
}
```
