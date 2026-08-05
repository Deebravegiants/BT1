### Title
Silent loss of paid on-demand orders during V1→V2 migration when legacy queue size exceeds the new `ON_DEMAND_MAX_QUEUE_MAX_SIZE` - (File: `polkadot/runtime/parachains/src/on_demand/migration.rs`)

### Summary
`UncheckedMigrateToV2::on_runtime_upgrade` merges V1 `FreeEntries` and all `AffinityEntries` cores into a single V2 `OrderStatus::queue` via `try_push`, and simply `break`s with a `log::warn!` when the bounded queue is full [1](#0-0) . The capacity check that would prevent this data loss (`pre_upgrade` comparing `total_orders` against `ON_DEMAND_MAX_QUEUE_MAX_SIZE`) only runs under the `try-runtime` feature and is never invoked during a real, non-try-runtime chain upgrade [2](#0-1) .

### Finding Description
`v1::ON_DEMAND_MAX_QUEUE_MAX_SIZE` used by the legacy queue-index ordering is a huge constant (`1_000_000_000`) [3](#0-2) , whereas `pre_upgrade`'s overflow check compares the actual merged order count against the *current* `polkadot_primitives::ON_DEMAND_MAX_QUEUE_MAX_SIZE`, which bounds the new V2 single queue's capacity [4](#0-3) . Normal, unprivileged users placing legitimate `place_order_*` extrinsics before a runtime upgrade can thus accumulate a combined `FreeEntries + AffinityEntries` count that exceeds the new, smaller V2 capacity while remaining perfectly valid under V1's own (much larger) limits.

The critical gap is that `pre_upgrade`/`post_upgrade` are gated by `#[cfg(feature = "try-runtime")]` in the `UncheckedOnRuntimeUpgrade` trait impl [2](#0-1) . In a genuine on-chain runtime upgrade (not a try-runtime dry run), only `on_runtime_upgrade` executes. That function performs no equivalent capacity check before draining and merging the V1 queues — it collects all orders from `FreeEntries::take()` and `AffinityEntries::drain()` into `all_orders`, sorts them, and pushes them one by one into the new bounded `OrderStatus::queue` via `try_push`, stopping silently and logging a warning once the queue is full [5](#0-4) . Any orders beyond the new capacity are discarded permanently — the storage for them has already been taken/drained, so they cannot be recovered.

Because this only manifests during a live, production-mode runtime upgrade (the `try-runtime` guarded checks never run there), the safety net that exists in the code (the `pre_upgrade` bound check) is not actually enforced on a real chain, so a user-populated near-max V1 queue at upgrade time results in silent loss of already-paid orders rather than a hard failure or safe rejection.

### Impact Explanation
Users who placed legitimate on-demand orders (paying real fees) under V1 can have those orders silently dropped during the real V1→V2 migration if the combined V1 queue size exceeds the new, smaller V2 `ON_DEMAND_MAX_QUEUE_MAX_SIZE`, with no on-chain error, no refund, and no re-ordering mechanism — only a log line invisible to users and impossible to act on after the fact. This is a genuine loss of paid-for service for the affected paras, though it is scoped to the orders that exceed capacity (not necessarily full corruption of `OrderStatus` for all subsequent users, since the queue itself remains structurally valid post-migration, just under-populated).

### Likelihood Explanation
This requires the legacy V1 queues to have accumulated more total orders than the new V2 capacity limit at the exact moment a runtime upgrade migration runs — a state reachable purely through ordinary paid `place_order_*` extrinsic usage (no privilege needed), constrained only by the economics of the dynamic spot-price traffic mechanism and by however much smaller the new cap is relative to the legacy `1_000_000_000` bound. Triggering of the migration itself is a governance/runtime-upgrade event, but the precondition (queue overfill) is entirely attacker/user-controlled ahead of time, matching the scenario described.

### Recommendation
Move the capacity/overflow validation out of the `try-runtime`-only `pre_upgrade` and into `on_runtime_upgrade` itself (or add an unconditional check before draining), so that on a real upgrade the migration either (a) refuses to drop orders silently and instead retains excess orders in a spillover structure, or (b) fails safely / halts the upgrade with a clear, non-silent signal, rather than relying on `log::warn!` inside a `break` that discards already-taken storage. At minimum, `on_runtime_upgrade` should perform the same `total_orders > ON_DEMAND_MAX_QUEUE_MAX_SIZE` check as `pre_upgrade` unconditionally (not gated by `try-runtime`), and either refund/preserve overflow orders or refuse the migration deterministically.

### Proof of Concept
Extend `free_and_affinity_queues_merged` in `polkadot/runtime/parachains/src/on_demand/migration.rs`:
1. Populate `v1::FreeEntries` and multiple `v1::AffinityEntries` cores with a combined order count exceeding the current `polkadot_primitives::ON_DEMAND_MAX_QUEUE_MAX_SIZE` (but valid under the old `v1::ON_DEMAND_MAX_QUEUE_MAX_SIZE = 1_000_000_000`).
2. Call `UncheckedMigrateToV2::<Test>::pre_upgrade()` and assert it returns `Err(...)` (already correctly implemented — confirm this holds).
3. Separately, call `UncheckedMigrateToV2::<Test>::on_runtime_upgrade()` directly (bypassing `pre_upgrade`, simulating a real non-try-runtime chain upgrade) and assert that `OrderStatus::<Test>::get().queue.len() < total_orders_inserted`, proving orders were silently dropped with no error raised to the caller.
4. Assert no mechanism exists to recover or detect the dropped orders on-chain (e.g., no event emitted, no counter of dropped orders retained in storage).

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L32-33)
```rust
	/// Old value of ON_DEMAND_MAX_QUEUE_MAX_SIZE from v1.
	const ON_DEMAND_MAX_QUEUE_MAX_SIZE: u32 = 1_000_000_000;
```

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L171-179)
```rust
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

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L248-296)
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
```

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L310-319)
```rust
	#[cfg(feature = "try-runtime")]
	fn pre_upgrade() -> Result<alloc::vec::Vec<u8>, sp_runtime::TryRuntimeError> {
		Self::pre_upgrade()
	}

	#[cfg(feature = "try-runtime")]
	fn post_upgrade(state: alloc::vec::Vec<u8>) -> Result<(), sp_runtime::TryRuntimeError> {
		Self::post_upgrade(state)
	}
}
```
