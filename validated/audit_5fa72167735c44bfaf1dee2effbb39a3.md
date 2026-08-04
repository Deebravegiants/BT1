### Title
Double-application of a frame's pending storage diff to `ContractInfo` via `apply_pending_storage_changes` enables storage-deposit refund/charge miscalculation in reentrant nested calls - (File: substrate/frame/revive/src/metering/mod.rs / substrate/frame/revive/src/metering/storage.rs)

### Summary
`FrameMeter::apply_pending_storage_changes` (backed by `RawMeter::apply_pending_changes_to_contract`) mutates a contract's `ContractInfo` (`storage_bytes`, `storage_byte_deposit`, `storage_item_deposit`, etc.) to preview a still-pending diff before a nested frame is created, but it takes `&self` and deliberately does **not** clear the frame's own `Contribution::Alive(diff)`. When the same frame is later finalized (`finalize_own_contributions`/`absorb`), the identical `diff` is applied to `info` a second time. The two applications are only mathematically self-cancelling if nothing else touches `info` in between — but the entire point of calling `apply_pending_storage_changes` before spawning the nested frame is to let that nested frame (and any further reentrant sub-calls on the same contract) mutate the very same `ContractInfo` in between the preview and the final commit, which breaks the ratio-based refund calculation's implicit invariant.

### Finding Description
`Diff::update_contract` (see `substrate/frame/contracts/src/storage/meter.rs:151-215`, mirrored in `revive`'s storage diff logic used by `Contribution::update_contract`) computes refunds as a *ratio* of removed bytes/items to the contract's **current** `storage_bytes`/`storage_items` in `info`, then mutates `info` in place. This ratio calculation is scale-invariant only if `info` is not touched by anyone else between the "preview" application and the "final" application of the same diff.

`RawMeter::apply_pending_changes_to_contract` [1](#0-0)  explicitly documents that, unlike `finalize_own_contributions`, it "does not consume the pending diff, allowing the meter to continue tracking changes after the nested call returns" — i.e. `own_contribution` remains `Contribution::Alive(diff)` after the call. It is invoked from `FrameMeter::apply_pending_storage_changes` [2](#0-1)  right before a nested frame is spawned so the child can see the parent's not-yet-committed storage changes (PR #10920, referencing paritytech/contract-issues#213).

The pallet also has a "safe" counterpart, `RawMeter::bank_pending_changes` [3](#0-2) , whose doc comment states it "reset[s] `own_contribution` so finalize does not apply it a second time" — proof that the pallet authors are aware that leaving `own_contribution` un-reset after mutating `info` causes a double-application hazard. `apply_pending_storage_changes`/`apply_pending_changes_to_contract`, by contrast, is `&self` (cannot reset the frame's own state) and is used specifically in the nested-call-creation path where the shared `info` is guaranteed to be mutated again before the parent's diff is eventually finalized.

Exploit flow:
1. A contract call increases (or decreases) its own storage, recorded in the frame's `own_contribution` as `Contribution::Alive(diff)`.
2. Before making a nested/reentrant call (e.g., calling itself or another contract that touches the same `ContractInfo`), `apply_pending_storage_changes` is invoked, mutating `info.storage_bytes`/`storage_byte_deposit` to reflect `diff`, while `own_contribution` still equals `diff` (discarded return value, no real transfer yet).
3. The nested/reentrant frame performs further storage operations against the now-already-mutated `info` (e.g., clears storage, shifting `info.storage_bytes` further).
4. When the nested frame returns and the parent frame is later finalized/absorbed, `own_contribution` (still holding the original `diff`) is applied to `info` a **second time** via `finalize_own_contributions`/`absorb`. Because `info.storage_bytes`/deposit fields have since moved due to step 3's nested mutation, the ratio-based refund/charge computed in this second application is no longer the mathematically-cancelling counterpart of the discarded first computation — it is computed against a shifted denominator, producing a refund amount that does not correspond to the actual net physical storage change caused by `diff` alone.
5. This defective `own_deposit` feeds directly into `total_deposit`/`charges`, which are later paid out as real balance in `execute_postponed_deposits` [4](#0-3) .

Existing protections (limit checks in `finalize`, `max_charged` tracking in `absorb`) bound the *charge* side but do not bound refunds computed this way, since `max_charged` only tracks the historical maximum charge, not a lower bound preventing over-refund from a corrupted ratio calculation.

### Impact Explanation
An attacker-controlled contract can, through a self-reentrant call sequence (write storage → trigger nested call that further mutates the same contract's storage before the parent frame's pending diff is committed), cause the storage-deposit meter to compute and actually transfer (via `execute_postponed_deposits`) a refund/charge amount inconsistent with the real net storage change. In the worst case this lets the attacker extract more balance in refunds than was ever actually deposited/held for their contract, directly violating the invariant that user-controlled deposits must remain fully backed.

### Likelihood Explanation
Preconditions: an unprivileged contract deployed by any signed account that (a) writes/removes storage, (b) makes a nested/reentrant call into itself or another contract touching the same `ContractInfo` between the write and the frame's finalization, and (c) that reentrant call is on a path where `apply_pending_storage_changes` was invoked. This is entirely reachable through a normal `call`/`instantiate` extrinsic dispatched by any account — no privileged origin, governance, or node-level access required. Repeatability depends on being able to control the intervening storage delta precisely enough to shift the ratio favorably, which is feasible for a contract author crafting the call sequence deliberately.

### Recommendation
Ensure the pending diff previewed via `apply_pending_storage_changes` is applied to `info` exactly once for real accounting purposes. Either:
- Change `apply_pending_storage_changes` to also reset `own_contribution` to a "committed" baseline (mirroring `bank_pending_changes`) and track the delta separately so any future `finalize_own_contributions`/`absorb` call operates only on genuinely new changes since the preview, or
- Snapshot the diff at preview time and subtract/reconcile it explicitly before applying the final diff, so the ratio computation always uses a stable, single-application baseline regardless of intervening nested mutations to the same `ContractInfo`.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/metering/storage/tests.rs` (extending the existing `TestMeter`/`ChargingTestCase` harness used by `charging_works`/`termination_works`):
1. Create a root meter and a nested frame representing a contract call that adds storage (`Diff{bytes_added, items_added}`), recording `own_contribution`.
2. Call `apply_pending_storage_changes`/`apply_pending_changes_to_contract` on this frame to simulate the pre-nested-frame preview commit into a shared `ContractInfo`.
3. Create a second, inner nested frame from this frame and have it apply a further `Diff` (e.g., a removal) against the *same* `ContractInfo` that was just mutated in step 2, then absorb it back into the parent.
4. Finalize the outer frame (`finalize_own_contributions`) against the same `ContractInfo`, applying the original `diff` from step 1 a second time.
5. Assert that the total deposit actually paid out via `execute_postponed_deposits` (sum across `own_deposit`s recorded in `charges`) never exceeds the sum of net `charge_deposit`/`record_contract_storage_changes` calls made across the whole simulated call tree — i.e. assert `execute_postponed_deposits(..)` never returns `Deposit::Refund(x)` where `x` is greater than what a single, non-reentrant application of the same diffs would have produced. The expectation is that this assertion **fails** with the current implementation, demonstrating the over-refund.

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L385-444)
```rust
	pub fn execute_postponed_deposits(
		&mut self,
		origin: &Origin<T>,
		exec_config: &ExecConfig<T>,
	) -> Result<DepositOf<T>, DispatchError> {
		// Only refund or charge deposit if the origin is not root.
		let origin = match origin {
			Origin::Root => return Ok(Deposit::Charge(Zero::zero())),
			Origin::Signed(o) => o,
		};

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

		Ok(self.total_deposit.clone())
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
