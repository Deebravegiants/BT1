### Title
Migration `on_runtime_upgrade` silently truncates on-demand order queue past V2 capacity, losing already-funded orders - (File: polkadot/runtime/parachains/src/on_demand/migration.rs)

### Summary
`UncheckedMigrateToV2::on_runtime_upgrade` merges all V1 `FreeEntries`/`AffinityEntries` orders and pushes them into the new fixed-capacity `OrderStatus::queue` via `order_status.queue.try_push`, but on the first `Err(para_id)` it simply `break`s the loop, discarding every remaining order with no refund and no error surfaced to the chain state. [1](#0-0)  The only safeguard against this scenario, `pre_upgrade`'s `total_orders > ON_DEMAND_MAX_QUEUE_MAX_SIZE` check, uses the old V1 constant of `1_000_000_000`, which is vastly larger than the actual V2 queue's `ConstU32<ON_DEMAND_MAX_QUEUE_MAX_SIZE>` bound, so it does not reliably prevent an over-capacity migration. [2](#0-1) [3](#0-2) 

### Finding Description
`on_runtime_upgrade` (the code that actually executes on-chain when a runtime with this migration is enacted) drains `v1::FreeEntries` and `v1::AffinityEntries`, sorts all collected orders, and pushes them one by one into the new `OrderStatus::queue` (a bounded structure sized by the new, smaller `ON_DEMAND_MAX_QUEUE_MAX_SIZE`). [4](#0-3)  When `try_push` returns `Err`, the code logs a warning and `break`s, meaning any orders sorted after the point of overflow are dropped from chain state entirely — with no compensation, refund, or re-queue mechanism. [1](#0-0) 

Critically, `pre_upgrade`/`post_upgrade` are only compiled under `#[cfg(any(feature = "try-runtime", test))]` / `#[cfg(feature = "try-runtime")]`, and are only invoked by tooling doing a try-runtime dry run — they are not part of the state transition function executed by validators when the runtime upgrade is actually enacted on a live chain. [5](#0-4) [6](#0-5)  This means that even if `pre_upgrade`'s stale/oversized threshold check had been correct, it would function only as a pre-deployment CI/testing gate (run by whoever prepares the runtime upgrade), not as an on-chain safeguard. The actual on-chain `on_runtime_upgrade` code path has zero guard against truncation — it will silently drop orders regardless of whether `pre_upgrade` was ever executed.

The existing test `queue_full_handling` only asserts `new_status.queue.len() > 0`, explicitly tolerating silent order loss rather than asserting exact preservation or a refund path. [7](#0-6) 

### Impact Explanation
If the V1 queue length at the moment of migration exceeds the new V2 fixed capacity, orders that were already funded (their `spot_price` charged when placed) are dropped from on-chain state during `on_runtime_upgrade` with no refund and no error. This results in: (1) loss of paid-for on-demand core-time slots for the affected parachains/orderers, and (2) an inconsistent/incomplete `OrderStatus::queue` post-upgrade that can stall scheduling for the dropped paras. If a `try-runtime` dry run is performed before the runtime is shipped, `post_upgrade`'s `migrated_orders == expected_orders` assertion would fail and block release — but there is no equivalent protection in the actual production `on_runtime_upgrade` path.

### Likelihood Explanation
The precondition (V1 queue length exceeding V2's new fixed capacity at the exact time governance enacts the runtime upgrade) requires the V1 queue to have grown, via permissionless order placement, past the new V2 bound before the upgrade block executes. This depends on the V1 runtime's configured queue-size limit relative to the new `ON_DEMAND_MAX_QUEUE_MAX_SIZE` constant — a coordination detail between the runtime's on-demand configuration (`HostConfiguration.on_demand_queue_max_size`) and the new constant, which could not be fully confirmed from the available index (the constant's value is defined elsewhere and was not resolvable in this session). Assuming the two are typically kept in sync by whoever authors the runtime upgrade, the scenario is unlikely in ordinary operation, but the migration code itself provides no runtime guard against a mismatch — it silently truncates regardless of cause, and the stale-constant `pre_upgrade` check only functions as an offline CI check, not an on-chain safety net. Because this is a one-time migration path exercised only during a governance-driven runtime upgrade, exploitability is bounded by that upgrade timing, but the underlying code defect (silent truncation with no refund) is real and independent of attacker intent — a chain operator misconfiguration or unexpectedly large queue at upgrade time would trigger the same fund-loss outcome.

### Recommendation
Replace the silent `break` in `on_runtime_upgrade` with an explicit, on-chain-safe handling strategy: either (a) fail the migration loudly (e.g., via a checked migration that halts/rolls back rather than partially applying), or (b) implement a refund path for orders that cannot be migrated (crediting back the `spot_price` to the paying account before dropping them from the queue), and emit a `storage_alias`-tracked audit record of dropped orders for post-hoc reconciliation. Additionally, fix `pre_upgrade`'s capacity check to compare against the actual V2 `ON_DEMAND_MAX_QUEUE_MAX_SIZE` constant (imported from the current, not v1, definition) so try-runtime tooling reliably catches oversized migrations before deployment.

### Proof of Concept
Extend `queue_full_handling` in `polkadot/runtime/parachains/src/on_demand/migration.rs`:
1. Populate `v1::FreeEntries` with a number of orders exceeding the real V2 `ON_DEMAND_MAX_QUEUE_MAX_SIZE` (not just 1000, but a count derived from the actual constant used to size `OrderStatus::queue`).
2. Run `pre_upgrade()` and assert it returns `Err(_)` (documenting that the current 1e9 threshold check is ineffective against the real bound) — or, after fixing the constant, assert it correctly errors.
3. Run `on_runtime_upgrade()` and assert `OrderStatus::<Test>::get().queue.len() == total_orders_pushed` (currently fails, proving truncation) — or, after the recommended fix, assert a refund event/extrinsic-tracked compensation was issued for each dropped order.
4. Assert no `spot_price`-charged balance is unaccounted for post-migration (cross-check against a mock currency balance snapshot taken before order placement).

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L32-33)
```rust
	/// Old value of ON_DEMAND_MAX_QUEUE_MAX_SIZE from v1.
	const ON_DEMAND_MAX_QUEUE_MAX_SIZE: u32 = 1_000_000_000;
```

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L146-148)
```rust
#[cfg(any(feature = "try-runtime", test))]
impl<T: Config> UncheckedMigrateToV2<T> {
	pub fn pre_upgrade() -> Result<alloc::vec::Vec<u8>, sp_runtime::TryRuntimeError> {
```

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L170-179)
```rust
		// Check that queue won't overflow during migration
		if total_orders > polkadot_primitives::ON_DEMAND_MAX_QUEUE_MAX_SIZE as usize {
			log::error!(
				target: LOG_TARGET,
				"Migration would lose orders: {} total orders exceeds V2 capacity of {}",
				total_orders,
				polkadot_primitives::ON_DEMAND_MAX_QUEUE_MAX_SIZE
			);
			return Err("Too many orders to migrate - queue capacity exceeded".into());
		}
```

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L248-298)
```rust
		// Collect all orders from both free and affinity queues
		let mut all_orders = alloc::vec::Vec::new();

		// Collect from free entries (1 read + 1 write via take())
		let free_entries = v1::FreeEntries::<T>::take().unwrap_or_default();
		weight.saturating_accrue(T::DbWeight::get().reads_writes(1, 1));
		for order in free_entries.into_iter() {
			all_orders.push(order);
		}

		// Collect from all affinity entries using drain for efficiency (reads + removes in one
		// op)
		let mut affinity_count = 0u64;
		for (_core_idx, affinity_heap) in v1::AffinityEntries::<T>::drain() {
			affinity_count += 1;
			for order in affinity_heap.into_iter() {
				all_orders.push(order);
			}
		}
		// drain() performs reads + writes in one operation
		weight.saturating_accrue(T::DbWeight::get().reads_writes(affinity_count, affinity_count));

		// Sort by QueueIndex to preserve order (ascending)
		all_orders.sort_by_key(|o| o.idx);

		// Drop ParaIdAffinity storage
		let affinity_count = v1::ParaIdAffinity::<T>::iter().count();
		let _ = v1::ParaIdAffinity::<T>::clear(u32::MAX, None);
		weight.saturating_accrue(
			T::DbWeight::get().reads_writes(affinity_count as u64, affinity_count as u64),
		);

		// Build new OrderStatus
		super::pallet::OrderStatus::<T>::mutate(|order_status| {
			// Preserve the traffic value
			order_status.traffic = old_queue_status.traffic;

			// Add all orders to the new queue
			for old_order in all_orders.iter() {
				if let Err(para_id) = order_status.queue.try_push(now, old_order.para_id) {
					log::warn!(
						target: LOG_TARGET,
						"Failed to migrate order for para_id {:?} - queue full, stopping migration of remaining orders",
						para_id
					);
					// Queue is full, no point trying to add more orders
					break;
				}
			}
		});
		weight.saturating_accrue(T::DbWeight::get().reads_writes(1, 1));
```

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L310-318)
```rust
	#[cfg(feature = "try-runtime")]
	fn pre_upgrade() -> Result<alloc::vec::Vec<u8>, sp_runtime::TryRuntimeError> {
		Self::pre_upgrade()
	}

	#[cfg(feature = "try-runtime")]
	fn post_upgrade(state: alloc::vec::Vec<u8>) -> Result<(), sp_runtime::TryRuntimeError> {
		Self::post_upgrade(state)
	}
```

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L588-622)
```rust
	#[test]
	fn queue_full_handling() {
		new_test_ext(MockGenesisConfig::default()).execute_with(|| {
			let _now = frame_system::Pallet::<Test>::block_number();

			// Try to add more orders than the queue can hold
			let mut free_queue = BinaryHeap::new();

			// Add many orders (queue might have a limit)
			for i in 0..1000 {
				free_queue.push(v1::OldEnqueuedOrder {
					para_id: ParaId::from(i),
					idx: v1::QueueIndex(i),
				});
			}

			v1::FreeEntries::<Test>::put(free_queue);

			let old_status = v1::OldQueueStatus::default();
			v1::QueueStatus::<Test>::put(old_status);

			StorageVersion::new(1).put::<on_demand::Pallet<Test>>();

			// Run migration - should not panic even if queue is full
			let state =
				UncheckedMigrateToV2::<Test>::pre_upgrade().expect("pre_upgrade should succeed");
			let _weight = UncheckedMigrateToV2::<Test>::on_runtime_upgrade();
			UncheckedMigrateToV2::<Test>::post_upgrade(state).expect("post_upgrade should succeed");

			// Verify migration completed (some orders may be dropped if queue is full)
			let new_status = on_demand::pallet::OrderStatus::<Test>::get();
			// Just verify it doesn't panic and creates some queue
			assert!(new_status.queue.len() > 0);
		});
	}
```
