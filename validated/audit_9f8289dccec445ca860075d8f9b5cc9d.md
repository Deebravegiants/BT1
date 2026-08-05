Audit Report

## Title
Terminated-contract address can be blocked from redeployment via strict-FIFO `DeletionQueue` head-of-line blocking (`PendingDepositCleanup`) - (File: `substrate/frame/revive/src/storage.rs`)

## Summary
`ContractInfo::new` rejects re-instantiation at an address while `NativeDepositOf` rows keyed by that address's fallback account still exist, and these rows are only cleared lazily by `process_deletion_queue_batch`, which drains the `DeletionQueueManager` strictly in FIFO order via `next()`/`delete_counter`. An attacker can pre-populate the queue with decoy `DeletionQueueItem`s ahead of a victim's entry so that the victim address stays under `PendingDepositCleanup` until all preceding decoys are fully drained.

## Finding Description
The code exactly matches the claim: `ContractInfo::new` blocks re-instantiation on `NativeDepositOf::iter_prefix` non-emptiness [1](#0-0) ; `process_deletion_queue_batch` processes only the head of the queue and `break`s on either phase failing to fully complete within budget, leaving the head entry in place for the next call [2](#0-1) ; and `DeletionQueueManager::next()`/`remove()` implement a strict ring-buffer FIFO advanced only one slot at a time upon full completion [3](#0-2) .

However, each `on_idle` call that reaches an entry does make monotonic forward progress on it: `NativeDepositOf::clear_prefix` and `child::kill_storage` both remove up to `key_budget` keys per call and are not reset, so repeated calls continue draining the same entry rather than stalling indefinitely on it, as confirmed by the phase-1/phase-2 logic [4](#0-3) . Crucially, once the victim's `DeletionQueueItem` is enqueued (at `insert_counter` at termination time), any new decoys the attacker creates afterward are appended *after* it, not before — `insert()` only appends at the tail [5](#0-4) . This means the delay is strictly bounded by the total size (native-deposit rows + trie keys) of decoys the attacker pre-committed *before* terminating the victim, not extensible afterward and not literally "indefinite."

## Impact Explanation
This is a real, reachable griefing vector: an unprivileged attacker can delay redeployment at a specific terminated address for a duration proportional to the volume of decoy storage/deposits they pre-seed ahead of the victim's queue entry. The delay is bounded and cost-scaled — it requires the attacker to actually create and fund (via real deposits) large `NativeDepositOf` prefixes and/or large child tries across multiple contracts/contributors, and the queue makes genuine incremental progress every `on_idle` call, so the block is finite and proportional to committed resources rather than a free/permanent DoS. This limits the severity below a permanent/unbounded denial-of-service; it is a temporary, resource-scaled delay of address reuse, primarily relevant to deterministic (e.g., CREATE2-style) redeployment flows.

## Likelihood Explanation
Triggerable via ordinary unprivileged extrinsics (instantiate, storage-growing calls, terminate/self-destruct), as referenced by the existing `MultiContributorStorage` test patterns [6](#0-5) . The attacker must lock real capital proportional to the desired delay (deposits for native rows and trie storage), and must front-load all decoys before terminating the victim address, since post-termination decoys are appended after the victim's entry and cannot extend the block further. This bounds both the feasibility and the maximum achievable delay to the attacker's committed deposit capacity.

## Recommendation
Decouple `PendingDepositCleanup` from full completion of the shared FIFO queue — e.g., eagerly clear (or perform a bounded first pass on) the terminated contract's own `NativeDepositOf` prefix and trie at termination time rather than relying purely on lazy `on_idle` draining, or maintain a per-entry resumable cursor combined with a bounded per-entry weight cap per `on_idle` call so a single large entry cannot fully occupy the queue head across many blocks, allowing subsequent entries (and address availability checks) to make independent progress.

## Proof of Concept
1. Instantiate N decoy contracts using `MultiContributorStorage`-style contracts, have K distinct contributor accounts call `growStorage` on each to seed large `NativeDepositOf` prefixes/tries.
2. Terminate all N decoys in order, each calling `queue_for_deletion` (`substrate/frame/revive/src/storage.rs:395-397`), enqueuing their `DeletionQueueItem`s.
3. Instantiate and terminate the victim contract at address `A` last, so its entry lands behind all N decoys.
4. Attempt to re-instantiate at `A`; assert failure with `Error::<Test>::PendingDepositCleanup` due to `substrate/frame/revive/src/storage.rs:210-212`.
5. Call `on_idle` repeatedly with a weight budget insufficient to drain all decoys in one call; verify `A` remains blocked until decoys ahead of it fully drain, and confirm the number of `on_idle` calls required scales with the pre-seeded decoy volume, then succeeds once decoys are cleared.

### Citations

**File:** substrate/frame/revive/src/storage.rs (L205-212)
```rust
		// Reject reuse of an address whose previous occupant still has unflushed
		// `NativeDepositOf` rows in the deletion queue. The on_idle drain will eventually
		// clear them; until it does, instantiating here would let the new contract inherit
		// stale per-payer entitlements.
		let account_id = T::AddressMapper::to_fallback_account_id(address);
		if NativeDepositOf::<T>::iter_prefix(&account_id).next().is_some() {
			return Err(Error::<T>::PendingDepositCleanup.into());
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

**File:** substrate/frame/revive/src/tests/deposit_payment.rs (L460-527)
```rust
/// A contract whose storage was paid for by two different signers, both via the native
/// fallback path, can still be terminated. [`Deposit::refund_all`] bypasses the per-payer
/// [`NativeDepositOf`] cap (one recipient at termination, contract gone), so the full native
/// hold goes to the terminator and any PGAS hold is settled via `settle_pgas_refund`.
#[test_case(FixtureType::Solc)]
#[test_case(FixtureType::Resolc)]
fn refund_all_drains_multi_contributor_native_hold(fixture_type: FixtureType) {
	let (code, _) = compile_module_with_type("MultiContributorStorage", fixture_type).unwrap();
	ExtBuilder::default().build().execute_with(|| {
		Balances::set_balance(&ALICE, 100_000_000_000);
		Balances::set_balance(&CHARLIE, 100_000_000_000);

		let Contract { addr, account_id } =
			builder::bare_instantiate(Code::Upload(code)).build_and_unwrap_contract();

		assert_ok!(
			builder::bare_call(addr)
				.data(MultiContributorStorage::growStorageCall {}.abi_encode())
				.build()
				.result,
		);
		assert_ok!(
			BareCallBuilder::<Test>::bare_call(RuntimeOrigin::signed(CHARLIE), addr)
				.data(MultiContributorStorage::growStorageCall {}.abi_encode())
				.build()
				.result,
		);

		let alice_entry = NativeDepositOf::<Test>::get(&account_id, &ALICE);
		let charlie_entry = NativeDepositOf::<Test>::get(&account_id, &CHARLIE);
		assert!(alice_entry > 0);
		assert!(charlie_entry > 0);

		let hold: <Test as Config>::RuntimeHoldReason = HoldReason::StorageDepositReserve.into();
		let native_held = Balances::balance_on_hold(&hold, &account_id);
		let pgas_held = AssetsHolder::balance_on_hold(PGAS_ASSET_ID, &hold, &account_id);
		assert_eq!(pgas_held, 0, "every charge fell back to native");
		assert_eq!(native_held, alice_entry + charlie_entry);

		let alice_before = Balances::balance(&ALICE);
		assert_ok!(
			builder::bare_call(addr)
				.data(
					MultiContributorStorage::terminateCall { beneficiary: DJANGO_ADDR.0.into() }
						.abi_encode(),
				)
				.build()
				.result,
		);
		let alice_after = Balances::balance(&ALICE);

		assert!(get_contract_checked(&addr).is_none(), "contract should be gone");
		assert_eq!(
			Balances::balance_on_hold(&hold, &account_id),
			0,
			"the full multi-contributor native hold has been released",
		);
		// ALICE receives the full storage-deposit hold (her own + CHARLIE's). The actual delta
		// also picks up the code-upload deposit refund and any tx-level deposit accounting,
		// so it is at least `native_held`.
		assert!(
			alice_after.saturating_sub(alice_before) >= native_held,
			"expected ALICE balance delta >= {}, got {}",
			native_held,
			alice_after.saturating_sub(alice_before),
		);
	});
}
```
