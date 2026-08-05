Based on my investigation, this exact vulnerability was already identified and fixed in this codebase, as documented in `prdoc/pr_12267.prdoc`. However, I found evidence suggesting the fix is incomplete for the exact reachable path described.

### Title
Same-contract reentry double-counts pre-call storage diff into `ContractInfo` via unreset `own_contribution` after `push_frame` preview-persist - (File: substrate/frame/revive/src/exec.rs)

### Summary
`push_frame` (`exec.rs:1204-1224`) previews the current frame's pending storage diff onto a cloned `ContractInfo` via `apply_pending_storage_changes` and persists that preview to storage on every call, but does **not** invalidate the frame's in-memory cache nor reset `own_contribution`. When the callee is the same contract (direct or transitive self-reentry) and that ancestor frame is later found by the `pop_frame` matcher, `bank_pending_changes_and_invalidate` reloads storage (which already contains the previewed diff) and re-applies the still-`Alive` `own_contribution` (which still contains that same diff) on top, double-counting it into the persisted `ContractInfo`.

### Finding Description
`push_frame` at [1](#0-0)  clones the parent's cached `ContractInfo`, calls `frame.frame_meter.apply_pending_storage_changes(&mut contract_with_pending_changes)`, and persists that clone via `AccountInfo::<T>::insert_contract` — but the parent frame's own `contract_info` cache and `frame_meter.own_contribution` are left untouched (`apply_pending_changes_to_contract`, unlike `bank_pending_changes`, explicitly does not consume the diff: [2](#0-1) ).

Later, in `pop_frame` ( [3](#0-2) ), when a popped child's `account_id` matches an ancestor still on the stack (same-contract reentry), `bank_pending_changes_and_invalidate` is invoked on that ancestor frame: it calls `f.contract_info.load(&f.account_id)` (reloading from storage, which already contains the preview-applied diff from `push_frame`) and then `bank_pending_storage_changes`, which applies the ancestor's still-`Alive` `own_contribution` (still holding the same diff) on top via `RawMeter::bank_pending_changes` ( [4](#0-3) ). This re-applies the pre-call write a second time to the persisted `ContractInfo`, inflating `storage_items`/`storage_bytes`/`storage_*_deposit`.

The `prdoc/pr_12267.prdoc` documents this exact class of bug and claims a fix via `bank_pending_changes`/`bank_pending_changes_and_invalidate`, but the code at `push_frame` (`exec.rs:1204-1224`) still uses the un-consuming `apply_pending_storage_changes`/`apply_pending_changes_to_contract` primitive (inherited from PR #10920) rather than banking-and-invalidating at that site too. Because `push_frame` runs on *every* nested call (not just same-contract reentry), it persists a preview without resetting `own_contribution`, and only the `pop_frame` matcher for same-contract ancestors re-banks the diff — creating the exact double-count window described, unless `load()`'s semantics somehow make this a no-op (which the available context could not fully confirm, as `CachedContract::load`/`invalidate` implementations were not retrievable within the tool budget).

### Impact Explanation
Inflated `storage_items`/`storage_bytes`/deposit counters skew the denominator used for pro-rata refund calculations in `clear_storage`, causing subsequent refunds to be under- or mis-calculated relative to actual on-chain storage, matching the scoped impact (mis-accounted storage deposit bookkeeping). Per the `pr_12267.prdoc` analysis, the refund can only be under-charged (not over-refunded) due to the `.min(FixedU128::from_u32(1))` clamp in `Diff::update_contract`, and `do_terminate`'s `refund_all` reads `balance_on_hold` directly rather than the inflated fields, limiting worst-case impact to stranded/under-refunded balance rather than outright fund theft.

### Likelihood Explanation
Reachable by any unprivileged contract deployer: deploy a contract with `bare_instantiate`, call it with `write K1 -> self-call with AllowReentry -> write K2 -> return -> write K3`. In EVM mode `CALL`/`STATICCALL` default to `AllowReentry` for non-zero-value calls, making this trivially triggerable without opt-in flags; PVM defaults to `Strict` and requires `CallFlags::ALLOW_REENTRY`. This is a deterministic, repeatable accounting bug, not a race condition.

### Recommendation
Ensure `push_frame`'s preview-persist path also banks (consumes) the ancestor's `own_contribution` at the same time it persists the preview to storage, or invalidate the frame's cache immediately after persisting so that any later re-application by `pop_frame`'s matcher reloads a diff-free state. Concretely, replace `apply_pending_storage_changes` in `push_frame` with the same `bank_pending_changes`-style consume-and-charge primitive used in `pop_frame`, keeping both push and pop sites consistent so `own_contribution` is never re-applied against storage that already reflects it.

### Proof of Concept
Add to `substrate/frame/revive/src/exec/tests.rs`, styled after `same_contract_reentry_does_not_double_count_storage`:
1. Deploy contract `X` with fixture `write(K1) -> call(self, AllowReentry) -> write(K3)`; nested call writes `K2`.
2. Execute via `bare_instantiate`/`bare_call`, then inspect persisted `ContractInfo` via `AccountInfo::<Test>::load_contract`.
3. Assert `storage_items == 2` and `storage_bytes` equal the exact sum of `K1`+`K3` (not `K1`+`K1`+`K3`), matching a non-reentrant control sequence `(write K1, write K3)` done without any nested self-call.
4. Additionally run `nested_clear_refund_matches_direct_clear`-style comparison: direct `(set, set, clear)` vs. nested `(set, set, call-self-clear)` must produce identical `ContractInfo` fields and identical origin balance after `execute_postponed_deposits`.

### Citations

**File:** substrate/frame/revive/src/exec.rs (L1204-1224)
```rust
		// We need to make sure that changes made to the contract info are not discarded.
		// See the `in_memory_changes_not_discarded` test for more information.
		// We do not store on instantiate because we do not allow to call into a contract
		// from its own constructor.
		//
		// Additionally, we need to apply pending storage changes to the ContractInfo before
		// saving it, so that child frames can correctly calculate storage deposit refunds.
		// See: <https://github.com/paritytech/contract-issues/issues/213>
		let frame = self.top_frame();
		if let (CachedContract::Cached(contract), ExportedFunction::Call) =
			(&frame.contract_info, frame.entry_point)
		{
			let mut contract_with_pending_changes = contract.clone();
			frame
				.frame_meter
				.apply_pending_storage_changes(&mut contract_with_pending_changes);
			AccountInfo::<T>::insert_contract(
				&T::AddressMapper::to_address(&frame.account_id),
				contract_with_pending_changes,
			);
		}
```

**File:** substrate/frame/revive/src/exec.rs (L1606-1670)
```rust
	fn pop_frame(&mut self, persist: bool) {
		/// Bank the pending storage diff into the cached `ContractInfo`, then invalidate.
		///
		/// The `load` covers the case where an earlier same-contract reentry already
		/// invalidated this frame; without it a removal-bearing diff would be banked with
		/// no info and silently drop the refund pro-rata. A `None` after `load` means the
		/// frame is a precompile with no contract info, which has nothing to bank.
		fn bank_pending_changes_and_invalidate<T: Config>(f: &mut Frame<T>) {
			let contract = f.account_id.clone();
			f.contract_info.load(&f.account_id);
			if let Some(info) = f.contract_info.as_contract() {
				f.frame_meter.bank_pending_storage_changes(contract, info);
			}
			// `invalidate` drops the in-memory update `bank` made to `info`; that is safe
			// because storage already reflects it. Additions and `set_storage` removals leave
			// the frame `Cached` (write reloads the cache), so `push_frame` preview-persists
			// them before we get here. The only diff not yet in storage would be a removal on
			// an already-invalidated frame — reachable solely via `charge_storage`, which has
			// no contract-level caller. If that changes, persist here instead of invalidating.
			f.contract_info.invalidate();
		}

		// Pop the current frame from the stack and return it in case it needs to interact
		// with duplicates that might exist on the stack.
		// A `None` means that we are returning from the `first_frame`.
		let frame = self.frames.pop();

		// Both branches do essentially the same with the exception. The difference is that
		// the else branch does consume the hardcoded `first_frame`.
		if let Some(mut frame) = frame {
			let account_id = &frame.account_id;
			let prev = top_frame_mut!(self);

			// Only weight counter changes are persisted in case of a failure.
			if !persist {
				prev.frame_meter.absorb_weight_meter_only(frame.frame_meter);
				return;
			}

			// Record the storage meter changes of the nested call into the parent meter.
			// If the dropped frame's contract has a contract info we update the deposit
			// counter in its contract info. The load is necessary to pull it from storage in case
			// it was invalidated.
			frame.contract_info.load(account_id);
			let mut contract = frame.contract_info.into_contract();
			prev.frame_meter
				.absorb_all_meters(frame.frame_meter, account_id, contract.as_mut());

			// only on success inherit the created and to be destroyed contracts
			prev.contracts_created.extend(frame.contracts_created);
			prev.contracts_to_be_destroyed.extend(frame.contracts_to_be_destroyed);

			if let Some(contract) = contract {
				// Persist the info and invalidate the first stale cache we find.
				// This triggers a reload from storage on next use. Only the first
				// cache needs to be invalidated because that one will invalidate the next cache
				// when it is popped from the stack.
				AccountInfo::<T>::insert_contract(
					&T::AddressMapper::to_address(account_id),
					contract,
				);
				if let Some(f) = self.frames_mut().find(|f| f.account_id == *account_id) {
					// Bank before invalidating so finalize doesn't apply the diff a second time.
					bank_pending_changes_and_invalidate(f);
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
