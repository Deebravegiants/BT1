### Title
Head-of-queue contract with inflated `NativeDepositOf` row count can indefinitely stall the entire lazy `DeletionQueue`, blocking trie reclamation for itself and every other queued contract - ([File: substrate/frame/revive/src/storage.rs])

### Summary
`ContractInfo::process_deletion_queue_batch` processes the `DeletionQueue` strictly FIFO and never advances past the head entry until *both* its `NativeDepositOf` rows (Phase 1) and its child trie (Phase 2) are fully drained in one contiguous run of the loop. An attacker can inflate a single contract's distinct-payer count in `NativeDepositOf` cheaply and unboundedly, forcing Phase 1 to never finish within a block's weight budget, which causes the whole batch loop to `break` before even reaching Phase 2 — starving not only that contract's own trie deletion but every other contract queued behind it, for as many blocks as it takes to drain the attacker-inflated row count.

### Finding Description
`process_deletion_queue_batch` reads the queue head via `DeletionQueueManager::next()`, which returns the entry at `delete_counter` without advancing the counter [1](#0-0) . The counter only advances when `DeletionQueueEntry::remove()` is called [2](#0-1) , and `remove()` is only reached after Phase 2 (`child::kill_storage`) returns `AllRemoved` [3](#0-2) , which itself is only attempted after Phase 1 (`NativeDepositOf::clear_prefix`) reports `maybe_cursor.is_none()` [4](#0-3) .

Critically, when Phase 1 does not finish within the per-block weight budget, the code executes `break` [5](#0-4) . This `break` exits the entire outer `loop { ... }` (which is meant to iterate over multiple queue entries per block), not just the current entry's processing. Consequently, once the head-of-queue entry can't finish Phase 1 in a block, no further entries are inspected that block at all — the whole deletion queue is stalled, not just the stuck entry.

`NativeDepositOf[holder][payer]` rows are created whenever a storage-deposit charge for a contract falls back to native DOT because the payer lacks sufficient PGAS [6](#0-5) . There is no cap on the number of distinct payers per contract in this charge path. An unprivileged attacker can:
1. Deploy a contract with a storage-growing entry point.
2. Fund many distinct accounts (each without PGAS) and have each call the contract once, causing each to be recorded as a distinct `NativeDepositOf[contract][payer]` row.
3. Terminate the contract (e.g. via the `self_destruct` precompile, as exercised in existing tests), which calls `queue_for_deletion` and pushes a `DeletionQueueItem` to the tail of the FIFO queue [7](#0-6) .

Because the attacker controls the timing (e.g., terminating when the queue is otherwise empty, or simply queuing first), their bloated entry becomes and stays the head of the FIFO queue. Each block's `on_idle` drain re-attempts Phase 1's `clear_prefix` on that entry, removes only as many rows as the block's weight budget allows (bench numbers show measured cost scales per row, with benchmarks going up to 1024 rows per call) [8](#0-7) , and `break`s the whole loop whenever it can't finish — for as many blocks as it takes to exhaust the attacker-inflated row backlog. During all of those blocks, the attacker's own trie (Phase 2) is never touched, and every other contract's `DeletionQueueItem` queued behind it is also never touched, since `queue.next()` always returns the same un-advanced head.

The two-phase-per-entry design is intentional per the doc comments [9](#0-8) , but the code additionally couples this per-entry phase gating to the entire batch's control flow via the unconditional `break`, rather than skipping to the next entry or capping the drainable-per-block extent independently of a single entry's completion.

### Impact Explanation
An attacker can force the on-chain lazy deletion pipeline for pallet-revive contracts into a head-of-line-blocking state: their own contract's child trie remains fully populated in state (bloating PoV/state size) for as long as it takes on_idle to drain the attacker-inflated `NativeDepositOf` backlog, and — more severely — every other terminated contract's `DeletionQueueItem` behind it in the FIFO queue is also blocked from any reclamation during that entire period, regardless of how small or already-clean those other entries are. This directly matches the scoped impact: chain-wide state-size/PoV growth degradation via a stuck per-entry two-phase queue, with reclamation time for a trie being dependent on an unrelated, attacker-controlled backlog on a queue entry that isn't even necessarily the caller's own.

### Likelihood Explanation
The exploit path uses only ordinary signed extrinsics: funding N accounts, having each make one contract call that triggers a native-fallback storage deposit, then calling a self-destruct entry point. No privileged origin, governance, or leaked keys are required. The cost to the attacker scales roughly linearly with N (extrinsic fees + minimal balances per sybil account), which is the same trade-off already acknowledged by the pallet's benchmarks (`deletion_queue_per_native_deposit_key` up to `k=1024`), but nothing bounds the attacker to a single-block-sized N — an attacker willing to spend more can grow N arbitrarily across many blocks before ever terminating the contract, then trigger a queue stall lasting proportionally many blocks. This is fully repeatable and deterministic given the FIFO/never-skip design.

### Recommendation
Change `process_deletion_queue_batch` so that an entry whose Phase 1 (or Phase 2) is not fully drained within the current block's budget does not block subsequent, independent queue entries from being processed in the same or later blocks — e.g., decouple per-entry phase completion from the outer loop's control flow (continue to the next entry instead of breaking the whole loop when only budget for the *current* entry is exhausted), or process entries out of strict FIFO order so a slow entry doesn't stall the queue, while still bounding total weight consumed per block.

### Proof of Concept
Integration test in `substrate/frame/revive/src/tests/pvm.rs` (or `deposit_payment.rs`):
1. Instantiate contract A with a trivially small trie (few keys) and terminate it, queuing it as `DeletionQueueItem` #0.
2. Instantiate contract B, have a large number of distinct signed accounts (e.g. 200+) each make one native-fallback storage-growing call to B so `NativeDepositOf[B]` has 200+ rows, then terminate B, queuing it as `DeletionQueueItem` #1 (after A).
3. Actually, to test the "unrelated resource" claim directly per the question, reorder: queue B (bloated `NativeDepositOf`, small trie) *before* A (clean, small trie, no `NativeDepositOf` rows). Run `Contracts::on_idle` (or `ContractInfo::process_deletion_queue_batch`) repeatedly with a fixed small `WeightMeter` limit for many blocks.
4. Assert: number of blocks until A's trie (`DeletionQueueItem` #1) becomes fully removed is proportional to B's `NativeDepositOf` row count, and that during those blocks `DeletionQueue::<Test>::iter()` still contains A's item even though A's own trie size is trivial — i.e., `child::get` on A's trie keys still returns values, and `DeletionQueue` count for A doesn't decrease, purely because B (ahead of it in the queue) hasn't finished Phase 1.
5. Expected (failing) assertion: "blocks-to-reclaim for A's trie is independent of B's `NativeDepositOf` backlog" — the test should show A's reclaim time scales with B's row count, proving the invariant violation.

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

**File:** substrate/frame/revive/src/storage.rs (L440-457)
```rust
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
```

**File:** substrate/frame/revive/src/storage.rs (L463-475)
```rust
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

**File:** substrate/frame/revive/src/storage.rs (L557-562)
```rust
/// A contract queued for lazy cleanup.
///
/// Holds the data needed to drain both the contract's [`NativeDepositOf`] rows and its child
/// trie. Cleanup runs in two phases per batch (native rows first, then the trie); the entry
/// stays in the queue until both phases have finished for it.
#[derive(Encode, Decode, TypeInfo, MaxEncodedLen, CloneNoBound, DebugNoBound, PartialEq, Eq)]
```

**File:** substrate/frame/revive/src/storage.rs (L587-594)
```rust
impl<'a, T: Config> DeletionQueueEntry<'a, T> {
	/// Remove the contract from the deletion queue.
	fn remove(self) {
		<DeletionQueue<T>>::remove(self.queue.delete_counter);
		self.queue.delete_counter = self.queue.delete_counter.wrapping_add(1);
		<DeletionQueueCounter<T>>::set(self.queue.clone());
	}
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

**File:** prdoc/stable2606/pr_11847.prdoc (L54-56)
```text
      Charge semantics:
      - If the user has enough reducible PGAS, the full amount is paid in PGAS via `fungibles::MutateHold::transfer_and_hold`, which emits the `TransferOnHold` event. No DOT is touched.
      - Otherwise the charge falls through to DOT, and the contribution is recorded in `NativeDepositOf` so it can be refunded as DOT later.
```

**File:** substrate/frame/revive/src/benchmarking.rs (L167-193)
```rust
	/// Measures the cost of clearing one [`NativeDepositOf`] row during
	/// [`ContractInfo::process_deletion_queue_batch`]. Pre-populates the contract with `k`
	/// per-payer rows and queues the contract for deletion with `native_cleared = false` and
	/// an empty trie. The deletion queue then drains all rows in one go.
	#[benchmark(skip_meta, pov_mode = Measured)]
	fn deletion_queue_per_native_deposit_key(k: Linear<0, 1024>) -> Result<(), BenchmarkError> {
		use frame_benchmarking::v2::account;

		// Empty trie: zero items, zero bytes; we only want to measure native-deposit cleanup.
		let instance = Contract::<T>::with_storage(VmBinaryModule::dummy(), 0, 0)?;
		for i in 0..k {
			let payer: T::AccountId = account("payer", i, 0);
			NativeDepositOf::<T>::insert(&instance.account_id, &payer, BalanceOf::<T>::default());
		}
		ContractInfo::<T>::queue_for_deletion(
			instance.info()?.trie_id,
			instance.account_id.clone(),
		);

		#[block]
		{
			ContractInfo::<T>::process_deletion_queue_batch(&mut WeightMeter::new())
		}

		assert!(<DeletionQueue<T>>::iter().next().is_none(), "deletion queue should be drained",);
		Ok(())
	}
```
