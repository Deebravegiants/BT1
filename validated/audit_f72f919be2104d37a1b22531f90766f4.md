This confirms the claim precisely as stated. The code exhibits exactly the described behavior: `DeletionQueueManager::next` retrieves the entry strictly at `delete_counter` with no skip mechanism [1](#0-0) , `insert`/`remove` confirm strict FIFO ordering with no reordering capability [2](#0-1) , and `process_deletion_queue_batch`'s loop `break`s the entire batch when phase 1 (`NativeDepositOf` drain) or phase 2 (trie kill) isn't fully finished for the current head entry, never advancing to try the next entry with remaining weight [3](#0-2) .Audit Report

## Title
Unbounded `NativeDepositOf` row growth lets an attacker monopolize `ContractInfo::process_deletion_queue_batch`, starving all subsequently queued contracts' cleanup - (File: substrate/frame/revive/src/storage.rs)

## Summary
`process_deletion_queue_batch` processes the deletion queue as a strict FIFO, single-entry-at-a-time loop that `break`s the entire batch whenever the current head entry's `NativeDepositOf` drain or child-trie kill cannot finish within the remaining weight budget, rather than moving on to attempt the next queued entry. An attacker can cheaply inflate the number of distinct `NativeDepositOf::<T>` rows attributed to one contract via the native-fallback path in `charge_and_hold`, then terminate that contract so it sits at the head of the FIFO queue, causing every other queued contract's cleanup to stall for as many blocks as it takes to drain the inflated entry.

## Finding Description
`ContractInfo::queue_for_deletion` inserts entries into a strictly FIFO `DeletionQueueManager` via `insert`, which appends at `insert_counter` [4](#0-3) . `DeletionQueueManager::next` always returns the entry at `delete_counter`, with no ability to skip ahead [1](#0-0) , and an entry is only removed (advancing `delete_counter`) once fully processed [5](#0-4) .

`process_deletion_queue_batch`'s main loop pulls exactly one entry via `queue.next()`. For that entry it first drains `NativeDepositOf` rows via `clear_prefix` up to a computed `key_budget`; if `result.maybe_cursor.is_some()` (rows remain), it `break`s the whole batch. Only if phase 1 fully completes does it proceed to `child::kill_storage` for the trie, again `break`ing the batch on `SomeRemaining`, and only removing the entry from the queue when both phases finish in the same call [3](#0-2) . This confirms the `break` terminates the entire batch rather than proceeding to the next queued contract with leftover weight.

`NativeDepositOf` rows are created uncapped: `charge_and_hold` falls back to native currency and calls `record_native_deposit(from, to, amount)` whenever the payer's PGAS reducible balance is insufficient [6](#0-5) , and `record_native_deposit` unconditionally inserts/updates a `NativeDepositOf::<T>` row keyed by `(to, from)` with no limit on the number of distinct payer rows [7](#0-6) . Only the deposited *amount* is bounded by payer balance — the *row count* is unbounded and attacker-controlled by using many distinct payer accounts.

Existing guards — `deletion_budget`/`key_budget_for` — only bound work within the current head entry per call; they provide no fairness mechanism across entries, and there is no per-block cap forcing forward progression to the next queue item.

## Impact Explanation
Since the queue is strictly FIFO with no skip-ahead, any contract queued behind the attacker's inflated entry has its child-trie and native-deposit cleanup withheld for as many `on_idle` invocations (blocks) as required to drain the attacker's entry — proportional to attacker-chosen N and unbounded in principle. This is a genuine storage-cleanup/service-degradation issue: chain storage for unrelated, cheap-to-clean contracts remains un-reclaimed for a number of blocks controlled by the attacker, contradicting the intended lazy cleanup design documented in `queue_for_deletion`'s own comment that both the child trie and `NativeDepositOf` entries are "drained lazily in `on_idle`" [8](#0-7) .

## Likelihood Explanation
The attack path requires no privileged access: an attacker only needs to (1) instantiate a contract, (2) drive N distinct funded signer accounts each lacking sufficient PGAS to perform a storage-writing call against the contract (each triggering the native fallback and creating a distinct `NativeDepositOf` row), and (3) terminate the contract to queue it FIFO. This is fully attacker-controlled, repeatable, and scales linearly with attacker budget (N accounts × minor deposits + fees), with no existing rate-limit or row cap to prevent it.

## Recommendation
Modify `process_deletion_queue_batch`'s loop so that exhausting the weight budget on one entry's phase does not abort the whole batch — instead continue attempting subsequent queue entries with any leftover weight, or impose a fixed per-entry weight/key cap per call so remaining weight is guaranteed to be offered to later entries. Additionally, consider bounding the number of distinct `NativeDepositOf` payer rows a single contract can accumulate, or restructuring native-deposit accounting (e.g., aggregate/batched refund tracking) so termination cleanup cost cannot grow unboundedly with attacker-chosen payer count.

## Proof of Concept
Rust integration test in `substrate/frame/revive`:
1. Instantiate contract `A`; drive N distinct funded signer accounts (each with native balance but insufficient/no PGAS) to each perform a storage-writing call against `A`, each triggering `charge_and_hold`'s native fallback and producing a distinct `NativeDepositOf::<T>::get(A, payer_i)` row via `record_native_deposit`.
2. Instantiate a second, cheap contract `B` with a small trie, terminate it (queued after `A`), then terminate `A` (queued before `B`, FIFO).
3. Repeatedly call `ContractInfo::process_deletion_queue_batch` with a fixed weight limit matching a realistic per-block `on_idle` budget.
4. Assert `B`'s child trie and account data remain undeleted until `NativeDepositOf::iter_prefix(A)` is empty, and that the number of calls (blocks) required before `B` is drained grows linearly with N — demonstrating attacker-controlled starvation of `B`'s cleanup behind `A`'s inflated entry.

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

**File:** substrate/frame/revive/src/storage.rs (L433-476)
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
		}
```

**File:** substrate/frame/revive/src/storage.rs (L587-613)
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
```

**File:** substrate/frame/revive/src/storage.rs (L615-627)
```rust
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

**File:** substrate/frame/revive/src/deposit_payment.rs (L348-375)
```rust
	fn charge_and_hold(
		reason: HoldReason,
		src: Funds<T::AccountId>,
		to: &T::AccountId,
		amount: BalanceOf<T>,
	) -> DispatchResult {
		let from = match &src {
			Funds::Balance(from) | Funds::TxFee(from) => *from,
		};

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

		Ok(())
	}
```

**File:** substrate/frame/revive/src/deposit_payment.rs (L556-562)
```rust
	/// Record that user `from` contributed `amount` in native balance to contract `to`.
	/// Read by [`Self::refund_on_hold`] to cap the native portion of refunds.
	fn record_native_deposit(from: &T::AccountId, to: &T::AccountId, amount: BalanceOf<T>) {
		NativeDepositOf::<T>::mutate(to, from, |entitlement| {
			*entitlement = entitlement.saturating_add(amount);
		});
	}
```
