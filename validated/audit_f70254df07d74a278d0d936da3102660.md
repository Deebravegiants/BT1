Audit Report

## Title
Silent loss of paid on-demand orders during `UncheckedMigrateToV2::on_runtime_upgrade` when old-queue backlog exceeds new bounded-queue capacity - (File: polkadot/runtime/parachains/src/on_demand/migration.rs)

## Summary
`UncheckedMigrateToV2::on_runtime_upgrade` collects all v1 `FreeEntries`/`AffinityEntries` orders, sorts them by `QueueIndex`, and pushes them into the new bounded `OrderStatus::queue` via `try_push`. On the first `QueueFull` error it only logs a warning and `break`s, permanently discarding every remaining (higher-index / more recently placed) order with no refund, no event, and no adjustment to `Revenue`, which was already credited at v1 order-placement time.

## Finding Description
`on_runtime_upgrade` gathers orders from `v1::FreeEntries::take()` and drains `v1::AffinityEntries`, sorts them ascending by `QueueIndex`, then inserts them into the bounded queue in `OrderStatus`: [1](#0-0) 

The new queue is a `BoundedVec` capped at `ConstU32<ON_DEMAND_MAX_QUEUE_MAX_SIZE>`: [2](#0-1) 

The v1 storage had no such hard cap during normal operation (its `QueueIndex` wraps around a much larger bound of `1_000_000_000`, hardcoded as a comment/constant local to the migration module): [3](#0-2) 

On the first `try_push` failure, the loop `break`s and every subsequent (higher `QueueIndex`) order in the sorted vector is dropped without any refund mechanism, event emission, or `Revenue` adjustment — nothing in `on_runtime_upgrade` touches `Revenue`, and payment accounting occurred earlier at v1 `place_order` time, fully decoupled from migration success.

The overflow guard that could catch this precondition, `pre_upgrade`'s `total_orders > ON_DEMAND_MAX_QUEUE_MAX_SIZE` check, exists only under `#[cfg(any(feature = "try-runtime", test))]`, and is wired into the `UncheckedOnRuntimeUpgrade::pre_upgrade`/`post_upgrade` trait methods only under `#[cfg(feature = "try-runtime")]`: [4](#0-3) 
This mirrors the standard FRAME/Substrate `try-runtime` hook pattern used throughout the SDK — `pre_upgrade`/`post_upgrade` are dry-run/testing-only hooks and are never compiled into or invoked by the production runtime during an actual on-chain runtime upgrade; only `on_runtime_upgrade` (unconditionally compiled) executes on-chain. This is expected framework design, not something unique to this migration, but it does mean nothing on-chain prevents the drop described above if the precondition (backlog > new capacity) exists at upgrade time and the `try-runtime`-based CI/dry-run check was not run or was ignored before deployment.

The existing regression test explicitly only checks that some orders survived, not that dropped orders are accounted for or refunded: [5](#0-4) 

## Impact Explanation
If the v1 backlog (`FreeEntries` + `AffinityEntries`) exceeds the v2 bounded queue's capacity at the moment `MigrateV1ToV2` executes, the excess orders — specifically those with the highest `QueueIndex` (i.e., most recently placed) — are silently and permanently dropped from the new queue. Since `Revenue` was already collected at `place_order_allow_death`/`place_order_keep_alive` time and is never touched by this migration path, the affected accounts have paid for coretime they will never receive, with no compensating event, refund, or storage correction. This is a genuine, concrete fund-loss bug in the migration logic, confirmed by direct code reading.

## Likelihood Explanation
The precondition (backlog size exceeding the new queue's `ON_DEMAND_MAX_QUEUE_MAX_SIZE` capacity) can be produced entirely by ordinary, unprivileged `place_order_*` extrinsics, and an attacker could deliberately front-load a large backlog before an anticipated runtime upgrade. However, the actual data loss only manifests when a governance-authorized runtime upgrade executes `MigrateV1ToV2` on top of that state — a one-time, release-triggered event, not something continuously exploitable. In practice, Polkadot/Kusama release processes run `try-runtime` dry-runs (which do include the `pre_upgrade` overflow check) before deploying upgrades to production, which would normally surface this exact precondition before it can cause real loss; the vulnerability materializes only if that standard safety step is skipped or if the backlog is built up between the dry-run and actual deployment. This narrows real-world likelihood considerably, but does not eliminate it as a genuine gap in the on-chain code path itself.

## Recommendation
In `on_runtime_upgrade`, do not silently drop orders on `try_push` failure. Either (a) refund the spot-price payment for dropped orders out of `Revenue` and emit an event identifying the affected `para_id`s, or (b) make the migration itself infallible with respect to capacity by asserting (and aborting the upgrade, not just logging) that `all_orders.len() <= queue_capacity`, forcing operators to address the backlog before the bounded-queue migration can proceed. The overflow guard should not be gated exclusively behind `try-runtime`; equivalent enforcement should exist in the always-compiled `on_runtime_upgrade` path.

## Proof of Concept
1. In a test analogous to `queue_full_handling`, populate `v1::FreeEntries` with `N` orders (`N` > `ON_DEMAND_MAX_QUEUE_MAX_SIZE`), each carrying a distinct `para_id`, and pre-seed `Revenue` with an amount corresponding to `N` paid orders as `place_order` would have recorded under v1.
2. Run `UncheckedMigrateToV2::<Test>::on_runtime_upgrade()`.
3. Observe `OrderStatus::<Test>::get().queue.len() == ON_DEMAND_MAX_QUEUE_MAX_SIZE` (orders dropped).
4. Assert (currently failing) that `Revenue` was reduced by the dropped orders' cost, or that a refund/event was emitted for each of the `N - capacity` dropped `para_id`s. Today, `Revenue` is untouched and no such event is emitted, confirming the loss.

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L32-33)
```rust
	/// Old value of ON_DEMAND_MAX_QUEUE_MAX_SIZE from v1.
	const ON_DEMAND_MAX_QUEUE_MAX_SIZE: u32 = 1_000_000_000;
```

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

**File:** polkadot/runtime/parachains/src/on_demand/migration.rs (L617-620)
```rust
			// Verify migration completed (some orders may be dropped if queue is full)
			let new_status = on_demand::pallet::OrderStatus::<Test>::get();
			// Just verify it doesn't panic and creates some queue
			assert!(new_status.queue.len() > 0);
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L100-104)
```rust
/// All queued on-demand orders.
#[derive(Encode, Decode, TypeInfo)]
pub struct OrderQueue<N> {
	queue: BoundedVec<EnqueuedOrder<N>, ConstU32<ON_DEMAND_MAX_QUEUE_MAX_SIZE>>,
}
```
