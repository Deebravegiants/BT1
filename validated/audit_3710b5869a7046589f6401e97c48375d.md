### Title
Silent loss of paid on-demand orders during `UncheckedMigrateToV2::on_runtime_upgrade` when old-queue backlog exceeds new bounded-queue capacity - (File: polkadot/runtime/parachains/src/on_demand/migration.rs)

### Summary
`UncheckedMigrateToV2::on_runtime_upgrade` collects all v1 `FreeEntries`/`AffinityEntries` orders and pushes them into the new bounded `OrderStatus::queue` via `try_push`, but on the first `QueueFull` failure it simply logs a warning and `break`s, discarding all remaining orders with no refund path. Since payment (`Revenue`) was already collected at v1 `place_order` time and is untouched by the migration, any dropped order represents coretime that was paid for but never delivered and never refunded.

### Finding Description
`on_runtime_upgrade` gathers `all_orders` from `v1::FreeEntries` and `v1::AffinityEntries`, sorts them by `QueueIndex` ascending, then inserts them into the new bounded queue: [1](#0-0) 

On the first `try_push` failure (`QueueFull`), the loop `break`s, so every subsequent order in the sorted vector (i.e., the ones placed later chronologically, with higher `QueueIndex`) is silently dropped. No code path in this function touches `Revenue`, issues a refund, or emits any event for the dropped orders. Payment accounting for on-demand orders happens in `place_order_*` at v1 order-placement time (well before this migration runs), so the funds are already spent/recorded and are permanently decoupled from whether the order survives the migration.

The `pre_upgrade` check that would catch this precondition (`total_orders > ON_DEMAND_MAX_QUEUE_MAX_SIZE`) only exists under `#[cfg(any(feature = "try-runtime", test))]` and is invoked from `UncheckedOnRuntimeUpgrade::pre_upgrade` only under `#[cfg(feature = "try-runtime")]`: [2](#0-1) 
This means in a live chain's normal runtime-upgrade execution (not a try-runtime dry run), only `on_runtime_upgrade` (line 238) actually runs — the safety check is never enforced on-chain, so nothing stops the drop from happening in production.

The existing regression test acknowledges the gap without asserting correctness: [3](#0-2) 
It only checks `queue.len() > 0`, never checking that dropped orders correspond to any refund or that `Revenue` matches the number of orders actually retained.

### Impact Explanation
Any account that placed a v1 on-demand order (via `place_order_allow_death`/`place_order_keep_alive`, both are ordinary unprivileged, fee-paying extrinsics) whose order ends up past the new queue's capacity after sort-by-index has its coretime request permanently erased on the v1→v2 migration, while the DOT already collected into `Revenue` at order-placement time remains recorded as collected. The affected user receives no coretime and no refund — a direct, unrecoverable loss of paid funds with no compensating event or storage adjustment.

### Likelihood Explanation
Requires: (1) an accumulated v1 backlog in `FreeEntries`/`AffinityEntries` larger than the v2 bounded queue capacity, and (2) the runtime upgrade actually executing `MigrateV1ToV2` on top of that state. Precondition (1) is plausible in high-congestion periods or can be intentionally engineered by anyone with funds submitting many `place_order` extrinsics shortly before a scheduled runtime upgrade, since sorting by ascending `QueueIndex` means the latest-placed (highest-index) orders are the ones dropped first when capacity is exceeded — an unprivileged actor can therefore reliably position other users' or their own late orders to be the ones discarded. The migration trigger itself is a governance/runtime-upgrade event, but the vulnerable state (paid, unfulfilled, unrefunded orders) is fully produced by ordinary user extrinsics and is not caught by any on-chain check.

### Recommendation
In `on_runtime_upgrade`, when `try_push` fails, do not silently drop the order: either (a) refund the affected orders' spot price payment out of `Revenue`/the collection pot and emit a `OrderRefundedOnMigration` event with the `para_id`/index, or (b) size the new bounded queue capacity to be at least the maximum possible v1 backlog (or perform the migration only after asserting via a hard `defensive_assert!`/abort that `all_orders.len() <= queue_capacity`, failing the runtime upgrade rather than silently truncating). Also, do not gate the overflow guard behind `try-runtime`-only cfg; enforce it (or the refund) as part of the always-compiled `on_runtime_upgrade` path.

### Proof of Concept
Extend `queue_full_handling`:
1. Populate `v1::FreeEntries` with N orders (N > new queue capacity), each with a distinct `para_id`, and separately pre-seed `Revenue` (or an equivalent payment record) with an amount corresponding to N paid orders, mirroring what `place_order` would have done under v1.
2. Run `UncheckedMigrateToV2::<Test>::on_runtime_upgrade()`.
3. Assert `OrderStatus::<Test>::get().queue.len() == capacity` (some orders dropped).
4. Assert (currently failing) that the total paid-for-and-not-fulfilled order count equals `0`, i.e., either `Revenue` was reduced by the dropped orders' cost, or a refund/`OrderRefundedOnMigration` event was emitted for each of the `N - capacity` dropped `para_id`s — today no such event exists and `Revenue` is untouched, proving funds are lost.

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L281-297)
```rust
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

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L617-621)
```rust
			// Verify migration completed (some orders may be dropped if queue is full)
			let new_status = on_demand::pallet::OrderStatus::<Test>::get();
			// Just verify it doesn't panic and creates some queue
			assert!(new_status.queue.len() > 0);
		});
```
