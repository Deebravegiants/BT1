### Title
Single-ParaId order spam can monopolize the shared bounded on-demand queue, starving unrelated paras with `QueueFull` - (File: `polkadot/runtime/parachains/src/on_demand/mod.rs`)

### Summary
`OrderQueue::pop_assignment_for_cores` enforces "only one order per `ParaId` assigned per scheduling round" via a `popped: BTreeSet<ParaId>` dedup set, pushing all further same-`ParaId` orders into `remaining_orders`. Because the drain rate for any single `ParaId` is capped at exactly 1 assignment per round regardless of `num_cores`, while the shared queue capacity (`on_demand_queue_max_size`) is finite and global across all paras, an unprivileged account can repeatedly call the permissionless `place_order_*` extrinsics for one target `ParaId` to fill the queue up to its max size faster than it drains, causing `QueueFull` rejections for all other paras' legitimate orders.

### Finding Description
The on-demand order queue is a single, shared, finite-capacity structure (`on_demand_queue_max_size`, capped by `ON_DEMAND_MAX_QUEUE_MAX_SIZE`) [1](#0-0) . Placing an order is a normal, unprivileged, permissionless extrinsic path (`place_order_allow_death`, `place_order_keep_alive`, `place_order_with_credits`) that lets any signed account order coretime for *any* `ParaId`, not just one it owns [2](#0-1) .

The scheduling invariant documented at the top of the module states that only one order per `ParaId` can be assigned per round; all additional same-`ParaId` orders are deferred to `remaining_orders` [3](#0-2) . This is implemented in `pop_assignment_for_cores` via the `popped.insert(order.para_id)` dedup check that pushes duplicate-para entries back into the queue instead of assigning them.

The structural problem: the per-`ParaId` drain rate is hard-capped at 1 assignment/round no matter how many cores (`num_cores`) are actually available, but the queue's admission control (`QueueFull`) is based purely on aggregate queue length, with no per-`ParaId` quota or rate limit. This means:
1. An attacker (any signed account, no privilege needed) submits N orders for the same `ParaId` X in rapid succession/within one block.
2. Each round, only 1 of those N orders is consumable regardless of how many cores are idle, so N-1 remain in `remaining_orders`.
3. If the attacker continues to add new orders for X faster than the 1/round drain rate, the shared queue fills toward `on_demand_queue_max_size`.
4. Once full, `place_order_*` calls from unrelated accounts/paras fail with `QueueFull`, even though cores may be otherwise idle and would gladly service those unrelated orders.

The only economic disincentive is the spot-price mechanism, but it is calculated from aggregate queue traffic/length, not from a specific `ParaId`'s outstanding order count, so it does not specifically throttle single-para spam beyond the same generic price curve that also taxes legitimate demand.

### Impact Explanation
This is a queue-monopolization / griefing DoS: legitimate on-demand users for unrelated paras receive `QueueFull` and cannot place orders, even though the chain has spare core capacity, because the shared bounded queue is saturated with orders for a single `ParaId` that can only drain at 1/round by design. Recovery time is bounded by queue occupancy divided by 1/round (not by `num_cores`), so with `on_demand_queue_max_size` orders queued for one para, unrelated paras could be locked out for that many rounds.

### Likelihood Explanation
Feasible with unprivileged capital: the attacker needs enough balance or credits to pay for `on_demand_queue_max_size` orders (rising spot price acts as a cost multiplier but does not prevent the attack, only raises its price), and no special permission is required since orders can target any `ParaId`. Precondition of "small `num_cores` relative to order arrival rate" is not even required — the per-`ParaId` cap of 1/round applies regardless of core count, so the attack works even with many idle cores.

### Recommendation
Introduce a per-`ParaId` rate limit or fairness bound on how many outstanding orders for a single `ParaId` may occupy the shared queue at once (e.g., reject/refund excess orders for a `ParaId` beyond a small multiple of `num_cores`), or make the spot-price/backpressure mechanism sensitive to per-`ParaId` queue depth rather than only aggregate queue length, so that spamming a single para escalates cost specifically for that para without exhausting shared capacity for others.

### Proof of Concept
Integration/fuzz test in `polkadot/runtime/parachains/src/on_demand/tests.rs`:
1. Configure `on_demand_queue_max_size = M` (finite) and `num_cores = 2` (or larger, to show the cap is independent of `num_cores`).
2. From a single unprivileged account, call `place_order_allow_death` repeatedly for `ParaId(X)` until the queue length reaches `M` (or until `QueueFull`), asserting acceptance each time up to `M`.
3. Advance blocks calling `on_initialize`/`pop_assignment_for_cores` for several rounds; assert that queue length decreases by at most 1 per round (drain rate == 1 regardless of `num_cores`).
4. While queue is still near `M`, from a different account attempt `place_order_allow_death` for `ParaId(Y)`; assert it fails with `Error::QueueFull` despite idle cores, proving unrelated-para starvation.
5. Repeat with varying `num_cores` to show impact is independent of core count, confirming the per-`ParaId` drain cap — not core availability — is the bottleneck.

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L23-27)
```rust
//! The module uses a single queue for all on-demand orders. Orders are generally processed in the
//! order they are received, but with an important constraint: only one order per ParaId can be
//! assigned in each scheduling round. If multiple orders for the same ParaId exist in the queue,
//! only the first will be assigned, and subsequent orders for that ParaId will remain queued until
//! the next round.
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L50-50)
```rust
use polkadot_primitives::{Id as ParaId, ON_DEMAND_MAX_QUEUE_MAX_SIZE};
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L64-68)
```rust
pub trait WeightInfo {
	fn place_order_allow_death() -> Weight;
	fn place_order_keep_alive() -> Weight;
	fn place_order_with_credits() -> Weight;
}
```
