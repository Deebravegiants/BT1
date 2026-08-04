### Title
Storage-deposit under-charging via same-address terminate-then-recreate coalescing in `execute_postponed_deposits` - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
`RawMeter::<T,E,Root>::execute_postponed_deposits` coalesces `Charge` entries purely by `T::AccountId` equality after a `sort_by(|a,b| a.contract.cmp(&b.contract))`. If the same address is used by a terminated contract and then a freshly re-instantiated contract within one call stack/transaction, the merge logic treats the new contract's legitimate `Alive` deposit charge as residue of the dead contract and silently drops it from both `total_deposit` and the `E::charge` application loop.

### Finding Description
The coalescing block [1](#0-0)  groups `Charge` entries solely by `contract` account id. Within a group it merges pairwise in push order (a stable sort preserves relative order for equal keys). The merge match arm: [2](#0-1) 

treats `(Alive, Terminated)` and `(Terminated, Alive)` symmetrically: it subtracts the `Alive` side's `amount` from `self.total_deposit` and forces the merged state to `Terminated`. This is correct for the *intended* case — an `Alive` charge recorded for a contract earlier in the same lifetime, followed by that same contract's own `terminate()` — because `terminate()` already folds the contract's full remaining deposit into `total_deposit` as a single `Deposit::Refund(refunded)` at [3](#0-2) , so the intermediate per-write `Alive` charge for that dead contract must be voided to avoid double counting.

The logic breaks when a *new* contract is later instantiated at the **same address** (deterministic salt/code-hash address, allowed because `terminate` removes the `ContractInfo` for that account, clearing any "duplicate contract" check) within the same transaction/call stack, and that new contract accrues its own storage writes. The resulting `Charge{contract: A, Alive{new_amount}}` is pushed after the `Terminated` marker for the same `A`. During coalescing this hits the same `(Terminated, Alive)` branch: `new_amount` is subtracted from `total_deposit` and the merged entry stays `Terminated`, meaning:
- `total_deposit` (the value returned to the caller and ultimately reflected as the aggregate deposit change) is decremented by an amount that corresponds to a *live*, still-existing contract's genuine deposit need, not a refund.
- The bottom charge-application loops only call `E::charge` for `ContractState::Alive` entries [4](#0-3) , so the merged `Terminated` entry for `A` is skipped entirely — no `E::charge`/hold is ever placed for the new contract's storage deposit.

Meanwhile, the new contract's `ContractInfo` (`storage_byte_deposit`/`storage_item_deposit`) was already updated to reflect the deposit via `Diff::update_contract` during `absorb`/`finalize_own_contributions` [5](#0-4) , independent of whether the corresponding balance hold is actually placed. This creates exactly the asymmetry the question describes: the meter's bookkeeping (`ContractInfo` deposit fields) and the actual reserved balance (`E::charge` calls / `total_deposit`) diverge, and the divergence favors the origin (under-charging).

The code's own `debug_assert!` at [6](#0-5)  — "We never emit two terminates for the same contract" — shows the author's mental model assumed at most one lifetime per address per execution; it does not defend against an `Alive` charge appearing *after* a `Terminated` marker for a reused address, which is exactly the scenario here and is not guarded by any assertion or check.

### Impact Explanation
An unprivileged origin can avoid having balance placed on hold for storage deposits of a contract it re-instantiates at an address it previously owned and terminated, within the same transaction/call stack. The scoped impact is a storage-deposit accounting asymmetry: `execute_postponed_deposits`'s returned `total_deposit` and issued `E::charge` calls under-represent the real deposit obligation, letting the origin retain funds that should have been reserved on hold for the reborn contract's storage.

### Likelihood Explanation
Preconditions required: (1) contract termination via `seal_terminate` reachable from unprivileged contract code, (2) re-instantiation at the exact same address permitted because `terminate` clears the account's `ContractInfo` (removing any duplicate-address guard), and (3) both events occurring within one meter's charge-coalescing scope (i.e., before `execute_postponed_deposits` runs at the end of the outer extrinsic). Both `terminate` and `instantiate` are standard, unprivileged, extrinsic-reachable operations; a contract designed to self-terminate and be redeployed with the same salt/code within one transaction is a normal, repeatable pattern requiring no special privileges — only deliberate contract code. I was not able to directly inspect `substrate/frame/revive/src/exec.rs`'s instantiate/terminate integration in this pass to fully confirm the absence of an explicit same-transaction re-instantiation guard; this should be verified against `exec.rs`, but nothing in the metering code itself blocks it, and the existing unit tests (`termination_works` in `substrate/frame/revive/src/metering/storage/tests.rs`) only cover the single-lifetime terminate case, not the reuse-after-terminate case.

### Recommendation
Do not coalesce `Charge` entries by bare `T::AccountId` equality alone. Either (a) tag each `Charge` with a generation/lifetime identifier (e.g., incremented each time an address is (re)instantiated within the same meter) so merges only combine charges from the same lifetime, or (b) stop merging across a `Terminated` boundary altogether: once a `Terminated` marker is coalesced for an address, any subsequent `Alive` charge for that same address should be pushed as a new, independent `Charge` entry (not merged into the terminated one), preserving its own `E::charge` application and its own contribution to `total_deposit`.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/metering/storage/tests.rs` style, analogous to `termination_works`:
1. Build a `TestMeter` (Root). Create `nested0` for address `CHARLIE`, `.charge()` some diff, `finalize_own_contributions`, `meter.absorb(nested0, &CHARLIE, Some(&mut info))` — pushes `Charge{CHARLIE, Alive{amount1}}`.
2. Call `meter.terminate(CHARLIE, refunded)` — pushes `Charge{CHARLIE, Terminated}`.
3. Simulate re-instantiation at `CHARLIE`: build `nested0b`, `.charge()` a new diff representing fresh storage writes, `finalize_own_contributions`, `meter.absorb(nested0b, &CHARLIE, Some(&mut new_info))` — pushes `Charge{CHARLIE, Alive{amount2}}`.
4. Call `meter.execute_postponed_deposits(&Origin::from_account_id(ALICE), &ExecConfig::new_substrate_tx())`.
5. Assert: (a) `TestExtTestValue::get()` contains an `E::charge` call for `CHARLIE` with `Deposit::Charge(amount2)` (the new contract's real deposit) — currently it will NOT, exposing the bug; (b) the returned `total_deposit` should include `amount2`'s charge rather than having it silently subtracted.

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

**File:** substrate/frame/revive/src/metering/storage.rs (L396-429)
```rust
		// Coalesce charges of the same contract
		self.charges.sort_by(|a, b| a.contract.cmp(&b.contract));
		self.charges = {
			let mut coalesced: Vec<Charge<T>> = Vec::with_capacity(self.charges.len());
			for mut ch in mem::take(&mut self.charges) {
				if let Some(last) = coalesced.last_mut() {
					if last.contract == ch.contract {
						match (&mut last.state, &mut ch.state) {
							(
								ContractState::Alive { amount: last_amount },
								ContractState::Alive { amount: ch_amount },
							) => {
								*last_amount = last_amount.saturating_add(&ch_amount);
							},
							(ContractState::Alive { amount }, ContractState::Terminated) |
							(ContractState::Terminated, ContractState::Alive { amount }) => {
								// undo all deposits made by a terminated contract
								self.total_deposit = self.total_deposit.saturating_sub(&amount);
								last.state = ContractState::Terminated;
							},
							(ContractState::Terminated, ContractState::Terminated) => {
								debug_assert!(
									false,
									"We never emit two terminates for the same contract."
								)
							},
						}
						continue;
					}
				}
				coalesced.push(ch);
			}
			coalesced
		};
```

**File:** substrate/frame/revive/src/metering/storage.rs (L431-441)
```rust
		// refunds first so origin is able to pay for the charges using the refunds
		for charge in self.charges.iter() {
			if let ContractState::Alive { amount: amount @ Deposit::Refund(_) } = &charge.state {
				E::charge(origin, &charge.contract, amount, exec_config)?;
			}
		}
		for charge in self.charges.iter() {
			if let ContractState::Alive { amount: amount @ Deposit::Charge(_) } = &charge.state {
				E::charge(origin, &charge.contract, amount, exec_config)?;
			}
		}
```

**File:** substrate/frame/revive/src/metering/storage.rs (L450-456)
```rust
	pub fn terminate(&mut self, contract: T::AccountId, refunded: BalanceOf<T>) {
		self.total_deposit = self.total_deposit.saturating_add(&Deposit::Refund(refunded));
		self.charges.push(Charge { contract, state: ContractState::Terminated });

		// no need to recalculate max_charged here as the total consumed amount will just decrease
		// with this extra refund
	}
```
