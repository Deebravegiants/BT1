### Title
Unconditional storage-preview persist in `push_frame` is not rolled back when the previewing frame later reverts, allowing uncharged storage deposit inflation - ([File: substrate/frame/revive/src/exec.rs])

### Summary
`Executable::push_frame` unconditionally writes a preview of the parent frame's *pending* (unfinalized) storage diff directly into on-chain `ContractInfo` via `AccountInfo::<T>::insert_contract` before spawning any nested frame. If the parent frame subsequently fails/reverts, `pop_frame`'s revert path (`absorb_weight_meter_only`) only discards the in-memory meter state — it never reloads or re-persists the parent's `ContractInfo` to undo the earlier direct write. This lets an attacker-controlled contract retain the storage-byte/item accounting inflation from the preview without the corresponding deposit ever being charged.

### Finding Description
In `push_frame`, right before creating a nested frame, the current top frame's pending diff is preview-applied to a **clone** of its `ContractInfo` and written straight to storage: [1](#0-0) 

This is the fix for issue #213 (visibility of pending writes to nested frames for refund pro-rating), implemented via `FrameMeter::apply_pending_storage_changes`, which mutates a `ContractInfo` clone without consuming or finalizing the meter's `own_contribution`: [2](#0-1) [3](#0-2) 

The write via `AccountInfo::<T>::insert_contract` is a direct storage mutation, independent of the frame stack's success/failure bookkeeping. When the *frame that performed the preview* itself later fails (e.g., its own execution errors out after the nested call returns), `pop_frame` takes the revert branch, which discards only the weight meter and returns immediately — it does not reload/repersist `ContractInfo` to reverse the earlier preview write: [4](#0-3) 

Compare this to the success path (`persist == true`), which explicitly reloads, banks, and invalidates the cache to avoid double counting — no equivalent unwind exists for the failure path with respect to the already-persisted preview: [5](#0-4) 

The actual balance-side deposit charge is queued in the meter's `own_contribution`/`charges` and only realized later via `TransactionMeter::execute_postponed_deposits`: [6](#0-5) 

Because the reverting frame's meter (containing `own_contribution`) is dropped by `absorb_weight_meter_only`, no `Charge` is ever queued for the write that was nonetheless already persisted into `ContractInfo`'s byte/item/deposit fields by the direct `insert_contract` call in `push_frame`.

Exploit flow: an unprivileged contract `P`, invoked by an intermediary contract `G` using low-level call semantics that tolerate a sub-call revert (e.g., EVM-style `CALL` which returns a failure flag instead of propagating), writes storage (accumulating a pending diff in its own `FrameMeter`), then makes any nested call (to itself, another contract, or a precompile) — this satisfies the `CachedContract::Cached` + `ExportedFunction::Call` condition in `push_frame` and triggers the direct persist of `P`'s pending write into on-chain `ContractInfo`. `P` then deliberately fails (e.g., explicit revert opcode, out-of-resource condition scoped to `P`'s own frame) so its frame pops with `persist == false`. `G` swallows the failure and the overall extrinsic succeeds. The write inflated into `ContractInfo` at the direct-persist step is never rolled back, and the corresponding deposit charge recorded in `own_contribution` is discarded along with the rest of the reverting meter.

### Impact Explanation
The contract's persisted `ContractInfo` storage byte/item counters and deposit fields reflect a storage allocation that was never paid for (no balance placed on hold, and no `Charge` ever reaches `execute_postponed_deposits`). This is a concrete storage-deposit under-charge / free storage allocation for an unprivileged contract caller, matching the scoped impact. It can also corrupt later refund pro-rating (since refunds are computed against these persisted deposit fields), potentially compounding the imbalance on subsequent `clear_storage` operations.

### Likelihood Explanation
Feasible with only standard, permissionless contract deployment and a call pattern using low-level/try-catch call semantics (natively supported for EVM-compatible `CALL` in `pallet-revive`, and reachable in PVM contracts too since reentrancy/self-revert doesn't require special privilege). No proxy, multisig, or governance access needed — a single signed account deploying two ordinary contracts is sufficient. Repeatable on every call satisfying the pattern (write → nested call → self-revert → caller swallows failure).

### Recommendation
Do not perform the direct `AccountInfo::<T>::insert_contract` persist of a preview-applied clone in `push_frame` unconditionally. Instead, either (a) defer the persist until the previewing frame's own outcome (success/failure) is known, reverting the write if the frame fails, similar to `bank_pending_changes_and_invalidate` on the success path; or (b) make the revert branch of `pop_frame` (`absorb_weight_meter_only`) explicitly reload and re-persist the reverting frame's `ContractInfo` to the pre-preview state whenever a preview write was made for that account during the frame's lifetime.

### Proof of Concept
Rust integration test in `substrate/frame/revive/src/exec/tests.rs`:
1. Deploy contract `G` that performs a low-level call to `P` and ignores/swallows the call's success flag (returns success regardless).
2. Deploy contract `P` whose code: writes a storage key (e.g., 64 bytes), then makes a nested call to a trivial contract `C` (to trigger the `push_frame` preview-persist for `P`), then explicitly reverts (e.g., unconditional `unreachable`/revert opcode).
3. Dispatch the extrinsic calling `G`, assert it succeeds (`Ok`).
4. Read `P`'s on-chain `ContractInfo` (`storage_bytes`, `storage_items`, `storage_byte_deposit`, `storage_item_deposit`) and assert they equal the pre-call baseline (zero net change) — expected to FAIL, showing the inflated values from the aborted preview persist.
5. Assert `execute_postponed_deposits` output / origin balance shows no deposit charge/hold corresponding to the write — expected to show the write was never paid for, confirming the under-charge.

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

**File:** substrate/frame/revive/src/exec.rs (L1639-1643)
```rust
			// Only weight counter changes are persisted in case of a failure.
			if !persist {
				prev.frame_meter.absorb_weight_meter_only(frame.frame_meter);
				return;
			}
```

**File:** substrate/frame/revive/src/exec.rs (L1644-1671)
```rust

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
			}
```

**File:** substrate/frame/revive/src/metering/mod.rs (L565-594)
```rust
	/// Execute all postponed storage deposit operations.
	///
	/// Returns `Err(Error::StorageDepositNotEnoughFunds)` if deposit limit would be exceeded.
	pub fn execute_postponed_deposits(
		&mut self,
		origin: &Origin<T>,
		exec_config: &ExecConfig<T>,
	) -> Result<DepositOf<T>, DispatchError> {
		log::debug!(
			target: LOG_TARGET,
			"Transaction meter finishes: \
				weight_left={:?}, \
				deposit_left={:?}, \
				weight_consumed={:?}, \
				deposit_consumed={:?}, \
				eth_gas_consumed={:?}",
			self.weight_left(),
			self.deposit_left(),
			self.weight_consumed(),
			self.deposit_consumed(),
			self.eth_gas_consumed(),
		);

		if self.deposit_left().is_none() {
			// Deposit limit exceeded
			return Err(<Error<T>>::StorageDepositNotEnoughFunds.into());
		}

		self.deposit.execute_postponed_deposits(origin, exec_config)
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
