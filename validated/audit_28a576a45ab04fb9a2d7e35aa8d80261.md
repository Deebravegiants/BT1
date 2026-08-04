### Title
Double-application of pending storage diff in nested contract calls inflates/corrupts storage-deposit refund - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
`RawMeter::apply_pending_changes_to_contract` (storage.rs:503-510), exposed via `FrameMeter::apply_pending_storage_changes` (mod.rs:673-675), mutates a contract's `ContractInfo` using the frame's pending `own_contribution` diff but — unlike the sibling method `bank_pending_changes` (storage.rs:514-528), which explicitly resets `own_contribution` to `Default` after applying it — leaves `own_contribution` untouched. When the same frame is later finalized via `finalize_own_contributions` (storage.rs:488-494), the identical, still-`Alive` diff is applied to `ContractInfo` a second time through `Contribution::update_contract`, producing an accounting state that is inconsistent with the byte-for-byte deposit actually charged.

### Finding Description
The fix introduced in `pr_10920` adds `apply_pending_storage_changes`/`apply_pending_changes_to_contract` so that a parent frame's pending storage diff becomes visible in `ContractInfo` before a nested call is dispatched, letting the nested frame compute correct refunds against up-to-date byte/item counts: [1](#0-0) 

Note that this function reads `own_contribution` (`Contribution::Alive(diff)`) and calls `diff.update_contract::<T>(Some(info))`, but does not reset or consume `own_contribution` afterward — the comment explicitly states "this does not consume the pending diff, allowing the meter to continue tracking changes after the nested call returns."

Compare this to the sibling method used for banking deposits at the end of a call stack: [2](#0-1) 

Here, after calling `update_contract`, `own_contribution` is explicitly reset to `Contribution::Alive(Default::default())` before returning, precisely to prevent a later `finalize`/`bank` call from re-applying the same diff.

`apply_pending_changes_to_contract` has no equivalent reset. Consequently, once a frame calls `apply_pending_storage_changes` (invoked by `exec.rs` right before creating a nested call frame, per the `pr_10920` prdoc's "Applied pending storage changes before nested frame creation in exec.rs (3 locations)"), the frame's `own_contribution` diff remains `Alive` and unconsumed. When that same frame is later finalized normally via `FrameMeter::finalize` → `finalize_own_contributions` (storage.rs:488-494), the *same* diff is applied to `ContractInfo` a second time: [3](#0-2) 

Since `ContractInfo`'s recorded storage-byte/item counters were already mutated by the first (pre-nested-call) application, the second application computes its refund/charge delta against an already-updated baseline rather than the original pre-call baseline — this is a double-application of state mutation to `ContractInfo`, not a no-op, because `update_contract` both (a) mutates counters on `info` and (b) returns a `Deposit` delta computed from the *current* counters at call time. Applying the same `diff` twice to a struct whose fields were already advanced by the first application does not yield the same numeric delta the second time; it can produce a refund/charge computed against a state that no longer reflects the actual byte delta caused by the frame, especially when a nested call (contract A writes N bytes, then a nested call into B/A itself deletes those bytes) interleaves with the pre-nested-call `apply_pending_storage_changes` call. The order of operations — apply diff early (for nested-frame visibility) without clearing it, then apply again at finalize — creates exactly the "double-counts or misses the parent's pending bytes" condition described in the question, because the second `update_contract` call operates on a baseline it did not originate from.

No caller-side guard prevents this: `exec.rs`'s three call sites invoke `apply_pending_storage_changes` unconditionally before nested dispatch, and normal frame teardown always calls `finalize`/`finalize_own_contributions` afterward regardless of whether `apply_pending_storage_changes` already ran for that frame. There is no flag on `RawMeter`/`ResourceMeter` distinguishing "already partially applied" frames from fresh ones.

### Impact Explanation
Because `ContractInfo`'s storage/deposit counters are advanced twice for the same logical diff while the underlying deposit-transfer/refund bookkeeping (`Contribution::update_contract`'s returned `Deposit`) is derived from the mutated counters at each call, the final `Deposit` returned to `execute_postponed_deposits`/`bank_pending_changes` can diverge from `per_byte * net_bytes_freed`. An attacker deploying two cooperating contracts (or a self-recursive one) can trigger the exact pattern the fix targeted — write N bytes, nested-call into a contract that deletes those bytes, return — driving `apply_pending_storage_changes` (pre-nested-call) and `finalize_own_contributions` (post-call) to both mutate `ContractInfo` from the same unconsumed diff, yielding a refund that does not match the actual net bytes freed. This is a fund-drain vector via inflated/incorrect storage-deposit refund, matching the scoped impact.

### Likelihood Explanation
No privileged access is required — a signed account can deploy the two contracts and issue the extrinsic that performs the nested `seal_call` sequence. The precondition (nested call clearing storage the parent just wrote) is exactly the scenario `pr_10920` was written to fix, and the asymmetric reset behavior between `apply_pending_changes_to_contract` and `bank_pending_changes` is a straightforward code-level oversight, not a contrived edge case — it is reachable on every nested call in pallet-revive after the fix landed, making it highly repeatable.

### Recommendation
Make `apply_pending_changes_to_contract` consume the pending diff the same way `bank_pending_changes` does — either reset `own_contribution` to `Contribution::Alive(Default::default())` after applying it, or track a separate "already-materialized-to-info" baseline so that `finalize_own_contributions` computes its delta against the post-`apply_pending_storage_changes` state rather than re-applying the full diff. Add a debug assertion (mirroring the one in `bank_pending_changes`) to catch any code path that finalizes a frame after `apply_pending_storage_changes` without proper reconciliation.

### Proof of Concept
Integration test in `substrate/frame/revive/src/exec/tests.rs` (or a new `#[test]` in `metering/storage/tests.rs`):
1. Deploy contract A and contract B (or a single self-recursive contract).
2. From an extrinsic, call A: A writes N bytes to its own storage (`seal_set_storage`), then A calls B (nested `seal_call`); B (or A itself, if self-recursive) deletes those N bytes in the nested frame; nested call returns success; outer frame finalizes.
3. Add a third-level nested call reproducing the same write/delete pattern to stress double-application across two intermediate frames.
4. Assert: `total refunded across the whole call stack == DepositPerByte::get() * net_bytes_freed`, computed independently via `RawMeter::charge` bookkeeping recorded by the test harness (e.g., track `Diff` inputs and compare against final balance change of the depositor).
5. Expected failure mode without the fix: refunded amount exceeds `DepositPerByte * net_bytes_freed` (or is inconsistent/negative-cost), demonstrating the double-application bug in `apply_pending_changes_to_contract`/`finalize_own_contributions`.

### Citations

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
