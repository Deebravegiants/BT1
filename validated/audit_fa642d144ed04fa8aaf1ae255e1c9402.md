This claim is verified against the actual code. `process_deletion_queue_batch` fetches only the FIFO head entry via `queue.next()` (which reads `delete_counter` directly, with `remove()` incrementing `delete_counter` only after full processing), runs Phase 1 (`NativeDepositOf::clear_prefix`) bounded by `key_budget`, and `break`s out of the entire outer `loop` when `result.maybe_cursor.is_some()` — never reaching Phase 2, and never advancing `delete_counter` to skip ahead to subsequent entries. [1](#0-0) [2](#0-1) 

The `NativeDepositOf` row is created per distinct payer whenever `charge_and_hold` falls back to native currency, and this fallback path is reachable by any unprivileged account whose PGAS balance is insufficient at deposit time. [3](#0-2) 

No cap on distinct-payer count per contract was found anywhere in the codebase (`grep` for `NativeDepositOf` usages across the repo shows no bounding logic), confirming the row count is attacker-controllable up to the number of distinct funded accounts an attacker arranges to pay into the target contract before termination.

This matches all the cited code precisely: the FIFO nature of `DeletionQueueManager` (single `delete_counter`/`insert_counter` pair, sequential `DeletionQueue` map keys), the two-phase gating in `process_deletion_queue_batch`, and the unconditional `break` on incomplete Phase 1 are all confirmed. The exploit path (unprivileged accounts triggering native-fallback deposits into a target contract, then terminating it) requires no privileged origin and is reachable through ordinary extrinsics. The impact — indefinite deferral of trie reclamation for the head entry and blocking of all subsequent queue entries — is a real, concrete state-bloat/DoS-style degradation of the lazy deletion mechanism, not a theoretical concern.

Audit Report

## Title
FIFO deletion-queue processing lets an inflated NativeDepositOf row count for one contract stall trie reclamation for that contract and block the entire queue - (File: substrate/frame/revive/src/storage.rs)

## Summary
`ContractInfo::process_deletion_queue_batch` processes queue entries strictly FIFO and requires Phase 1 (`NativeDepositOf::clear_prefix`) to fully finish for the head entry before Phase 2 (child-trie kill) even starts; when Phase 1 doesn't finish in a block, the code breaks the entire outer loop rather than skipping to the next entry. An attacker who inflates a contract's distinct native-deposit-payer count before terminating it can make Phase 1 alone consume the whole per-block deletion budget for many consecutive blocks, indefinitely deferring the contract's trie reclamation and blocking reclamation of every other queued contract behind it.

## Finding Description
`NativeDepositOf` rows are created per distinct payer whenever a storage deposit charge falls back to the native currency, via `record_native_deposit` called from `PGasDeposit::charge_and_hold` when the payer lacks sufficient reducible PGAS. [3](#0-2) 
This is fully attacker-controllable through ordinary extrinsics: an attacker's contract can be funded by many distinct accounts prior to termination, producing an arbitrarily large number of `(contract, payer)` rows for a single contract.

At deletion time, `queue_for_deletion` pushes a `DeletionQueueItem` containing both the `trie_id` and `account_id`. [4](#0-3) 
`process_deletion_queue_batch` fetches only the FIFO head via `queue.next()`, and for that head entry runs Phase 1 (`NativeDepositOf::clear_prefix`) bounded by `key_budget`; if `result.maybe_cursor.is_some()` (i.e., Phase 1 not finished), it `break`s out of the entire batch loop, never reaching Phase 2 for this entry, and never advancing to any subsequent queue entry either. Only once Phase 1 fully completes does Phase 2 (`child::kill_storage`) run. [1](#0-0) 

Because the queue has no mechanism to skip a stuck head entry and move to entries behind it (`delete_counter` only advances via `DeletionQueueEntry::remove`, which is only called after both phases succeed), an entry with a very large `NativeDepositOf` row count occupies the head of the queue for as many blocks as it takes to drain all its rows at the per-block `key_budget`, and during that span neither its own child-trie nor any subsequently queued contract's trie or deposits are touched. [2](#0-1) 

No upstream cap on distinct-payer count per contract was found in `deposit_payment.rs` or elsewhere.

## Impact Explanation
This produces state-size/PoV growth degradation: a contract's (potentially attacker-inflated) child-trie storage remains fully on-chain and unreclaimed for as long as its `NativeDepositOf` backlog takes to drain, and this also stalls reclamation of every other contract queued for deletion behind it, since the queue is strictly FIFO and a stuck head blocks all progress. This is a genuine violation of the deletion-queue invariant that reclamation should progress incrementally regardless of unrelated per-contract state size.

## Likelihood Explanation
Reachable entirely through unprivileged extrinsic paths: any signed account can pay storage deposits into a target contract (native fallback happens automatically when the payer lacks sufficient PGAS), and the contract owner/attacker terminates the contract afterward, pushing it (with its now-large `NativeDepositOf` backlog) into the deletion queue via `queue_for_deletion`. No governance or privileged origin is required — the attacker only needs sufficiently many distinct payer accounts to have contributed native-fallback deposits before termination.

## Recommendation
Decouple Phase 1 completion from queue-entry ordering: either (a) do not block the outer loop on an incomplete `NativeDepositOf` drain — continue to Phase 2 for that entry with remaining budget, and/or allow subsequent queue entries to make independent progress; or (b) cap the number of distinct `NativeDepositOf` payer rows a single contract can accumulate; or (c) allow the trie-kill phase to proceed for the head entry even while `NativeDepositOf` rows remain, only removing the entry from the queue once both are drained.

## Proof of Concept
Rust integration test in `substrate/frame/revive/src/tests.rs`:
1. Create contract A with a child trie of size `N` items and exactly 1 `NativeDepositOf` row.
2. Create contract B with an identical trie size `N` but `M` (large) distinct `NativeDepositOf` rows via `M` distinct signed accounts triggering native-fallback deposits into B before termination.
3. Terminate both contracts in the same block (test both orderings A-then-B and B-then-A).
4. Run `on_idle` for successive blocks, recording when each contract's child trie is fully removed.
5. Assert blocks-to-full-trie-reclaim for A and B should be equal since trie sizes match — this fails, showing B's reclamation (and A's, if B precedes A) is delayed proportional to `M`.

### Citations

**File:** substrate/frame/revive/src/storage.rs (L390-397)
```rust
	/// Push a contract's trie and account to the deletion queue for lazy removal.
	///
	/// You must make sure that the contract is also removed when queuing for deletion.
	/// Both the contract's child trie and any [`NativeDepositOf`] entries it held are drained
	/// lazily in `on_idle`.
	pub fn queue_for_deletion(trie_id: TrieId, contract: AccountIdOf<T>) {
		DeletionQueueManager::<T>::load().insert(DeletionQueueItem::new(trie_id, contract));
	}
```

**File:** substrate/frame/revive/src/storage.rs (L433-475)
```rust
		loop {
			let Some(entry) = queue.next() else { break };

			// Charge the per-entry overhead.
			let Some(after_entry) = remaining.checked_sub(&weight_per_entry) else { break };
			remaining = after_entry;

			// Phase 1: drain `NativeDepositOf` rows for this contract.
			let key_budget = key_budget_for(remaining, weight_per_native_key);
			if key_budget == 0 {
				break;
			}
			let result =
				NativeDepositOf::<T>::clear_prefix(&entry.value.account_id, key_budget, None);
			remaining = remaining
				.saturating_sub(weight_per_native_key.saturating_mul(u64::from(result.unique)));
			if result.maybe_cursor.is_some() {
				break;
			}

			// Phase 2: kill the child trie.
			let key_budget = key_budget_for(remaining, weight_per_trie_key);
			if key_budget == 0 {
				break;
			}
			#[allow(deprecated)]
			let outcome = child::kill_storage(
				&ChildInfo::new_default(&entry.value.trie_id),
				Some(key_budget),
			);
			match outcome {
				KillStorageResult::SomeRemaining(keys_removed) => {
					remaining = remaining
						.saturating_sub(weight_per_trie_key.saturating_mul(keys_removed.into()));
					break;
				},
				KillStorageResult::AllRemoved(keys_removed) => {
					remaining = remaining.saturating_sub(
						weight_per_trie_key.saturating_mul(u64::from(keys_removed)),
					);
					entry.remove();
				},
			};
```

**File:** substrate/frame/revive/src/storage.rs (L587-627)
```rust
impl<'a, T: Config> DeletionQueueEntry<'a, T> {
	/// Remove the contract from the deletion queue.
	fn remove(self) {
		<DeletionQueue<T>>::remove(self.queue.delete_counter);
		self.queue.delete_counter = self.queue.delete_counter.wrapping_add(1);
		<DeletionQueueCounter<T>>::set(self.queue.clone());
	}
}

impl<T: Config> DeletionQueueManager<T> {
	/// Load the `DeletionQueueCounter`, so we can perform read or write operations on the
	/// DeletionQueue storage.
	fn load() -> Self {
		<DeletionQueueCounter<T>>::get()
	}

	/// Returns `true` if the queue contains no elements.
	fn is_empty(&self) -> bool {
		self.insert_counter.wrapping_sub(self.delete_counter) == 0
	}

	/// Insert a contract in the deletion queue.
	fn insert(&mut self, value: DeletionQueueItem<T>) {
		<DeletionQueue<T>>::insert(self.insert_counter, value);
		self.insert_counter = self.insert_counter.wrapping_add(1);
		<DeletionQueueCounter<T>>::set(self.clone());
	}

	/// Fetch the next contract to be deleted.
	///
	/// Note:
	/// we use the delete counter to get the next value to read from the queue and thus don't pay
	/// the cost of an extra call to `sp_io::storage::next_key` to lookup the next entry in the map
	fn next(&mut self) -> Option<DeletionQueueEntry<'_, T>> {
		if self.is_empty() {
			return None;
		}

		let entry = <DeletionQueue<T>>::get(self.delete_counter);
		entry.map(|value| DeletionQueueEntry { value, queue: self })
	}
```

**File:** substrate/frame/revive/src/deposit_payment.rs (L358-372)
```rust
		if Self::pgas_reducible_balance(from) >= amount {
			<Holder as fungibles::MutateHold<T::AccountId>>::transfer_and_hold(
				Id::get(),
				&reason.into(),
				from,
				to,
				amount,
				Precision::Exact,
				Preservation::Expendable,
				Fortitude::Polite,
			)?;
		} else {
			<() as Deposit<T>>::charge_and_hold(reason, src, to, amount)?;
			Self::record_native_deposit(from, to, amount);
		}
```
