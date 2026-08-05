### Title
Single para can monopolize the entire on-demand `OrderQueue` capacity via repeated self-orders, denying queue access to all other parachains - ([File: polkadot/runtime/parachains/src/on_demand/mod.rs])

### Summary
`OrderQueue::try_push` (mod.rs lines 140–144) appends any incoming order to the shared `BoundedVec` up to `on_demand_queue_max_size` with no per-`ParaId` limit or de-duplication check at enqueue time. Because `pop_assignment_for_cores` (lines 108–131) only guarantees fairness *at pop time* (one dequeue per `ParaId` per round via the `popped: BTreeSet` de-dup), an attacker can pre-fill the entire bounded queue with orders for a single `para_id`, exhausting capacity for every other para until the backlog drains at a rate of one order per round.

### Finding Description
`OrderQueue` is a single, shared, capacity-bounded structure (`BoundedVec<EnqueuedOrder<N>, ConstU32<ON_DEMAND_MAX_QUEUE_MAX_SIZE>>`, mod.rs lines 100–104), and `try_push` simply does `self.queue.try_push(EnqueuedOrder { para_id, ordered_at: now })`, returning `Err` only when the vector is already at its bound (mod.rs lines 137–144) [1](#0-0) . There is no check comparing `para_id` against existing queued entries before insertion, so nothing stops the same `para_id` from occupying an arbitrary number of the bounded slots.

The module doc itself acknowledges the asymmetry: "only one order per ParaId can be assigned in each scheduling round... subsequent orders for that ParaId will remain queued until the next round" [2](#0-1) . This is confirmed by `pop_assignment_for_cores`, which iterates the queue and only pops the *first* ready order per `para_id` into the `popped` `BTreeSet` per invocation, leaving all other same-para orders in `remaining_orders` for future rounds [3](#0-2) .

The `Error::QueueFull` (mod.rs lines 253–255) is returned uniformly regardless of which `ParaId`s currently occupy the queue [4](#0-3) . Consequently, an attacker who controls sufficient `Credits::<T>` or free balance can call the signed extrinsics `place_order_with_credits` / `place_order_allow_death` / `place_order_keep_alive` repeatedly for their own `attacker_para_id`, filling all `on_demand_queue_max_size` slots. Every other para's genuine `place_order_*` call will then fail with `Error::QueueFull`, even though only one of the attacker's orders can ever be assigned per scheduling round — the rest sit idle, occupying space that legitimate paras could have used.

### Impact Explanation
This is a real, concrete denial-of-service against the on-demand blockspace market: all other parathreads are locked out of placing on-demand orders (`Error::QueueFull`) for as long as the attacker's backlog persists. Since the queue drains at only one entry per `ParaId` per scheduling round, an attacker who fills the full `on_demand_queue_max_size` can keep every other para locked out for `on_demand_queue_max_size` rounds (refilling as slots free up to keep the queue perpetually saturated), effectively seizing the shared queue resource for a single para. This matches the scoped impact: unauthorized resource seizure (blockspace queue griefing) against every other on-demand parachain.

### Likelihood Explanation
The attack requires only a signed account with enough balance or `Credits::<T>` to pay the (traffic-adjusted) spot price for `on_demand_queue_max_size` orders. Spot price rises with queue utilization (`SpotTrafficCalculationErr`/traffic multiplier logic in the same module), which raises the attacker's cost per additional order but does not prevent the attack — it only bounds how cheaply it can be sustained, and the attacker can maintain saturation indefinitely by re-ordering as slots free at the one-per-round drain rate while other paras remain shut out. No per-para enqueue cap, no origin/queue-position check, and no rate limit per `ParaId` exists to block this in the reachable extrinsic path.

### Recommendation
Introduce a per-`ParaId` cap on outstanding queued (unassigned) orders — e.g., reject `try_push` for a `para_id` that already has N ≥ configured limit (such as 1) unassigned entries in the queue, returning a dedicated error (e.g., `Error::ParaAlreadyQueued`/`TooManyOrdersForPara`) distinct from global `QueueFull`. This preserves the module's stated fairness invariant ("only one order per ParaId assigned per round") by also enforcing it at enqueue time, not merely at pop time.

### Proof of Concept
Rust integration test (extends `on_demand/tests.rs` patterns):
1. Configure `OnDemandQueueMaxSize` to a small bound (e.g., 5) via `configuration` pallet.
2. Fund `attacker` account (or credit via `Credits::<T>`) enough to cover 5 escalating spot-price orders for `attacker_para_id`.
3. Loop calling `Pallet::<T>::place_order_with_credits(attacker_origin, max_amount, attacker_para_id)` (or `place_order_allow_death`) until the queue reaches `on_demand_queue_max_size`; assert all 5 succeed and `OrderStatus::<T>::get().queue.len() == 5`.
4. Call `place_order_with_credits(victim_origin, max_amount, victim_para_id)` for a different `victim_para_id`; assert it returns `Err(Error::<T>::QueueFull)`.
5. Advance one scheduling round (call `pop_assignment_for_cores` via the scheduler flow with `num_cores = 1`); assert only one `attacker_para_id` entry is removed/assigned and 4 remain queued, still blocking `victim_para_id`.
6. Repeat step 4 after each round to show `victim_para_id` remains locked out until the attacker's full backlog (all entries for `attacker_para_id`) drains, quantifying rounds-blocked = queue size, confirming the DoS window.

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L23-27)
```rust
//! The module uses a single queue for all on-demand orders. Orders are generally processed in the
//! order they are received, but with an important constraint: only one order per ParaId can be
//! assigned in each scheduling round. If multiple orders for the same ParaId exist in the queue,
//! only the first will be assigned, and subsequent orders for that ParaId will remain queued until
//! the next round.
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L106-131)
```rust
impl<N> OrderQueue<N> {
	/// Pop `num_cores` from the queue, assuming `now` as the current block number.
	pub fn pop_assignment_for_cores<T: Config>(
		&mut self,
		now: N,
		mut num_cores: u32,
	) -> impl Iterator<Item = ParaId>
	where
		N: Saturating + Ord + One + Copy,
	{
		let mut popped = BTreeSet::new();
		let mut remaining_orders = Vec::with_capacity(self.queue.len());
		for order in mem::take(&mut self.queue) {
			// Order is ready 2 blocks later (asynchronous backing):
			let ready_at = order.ordered_at.saturating_plus_one().saturating_plus_one();
			let is_ready = ready_at <= now;

			if num_cores > 0 && is_ready && popped.insert(order.para_id) {
				num_cores -= 1;
			} else {
				remaining_orders.push(order);
			}
		}
		self.queue = BoundedVec::truncate_from(remaining_orders);
		popped.into_iter()
	}
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L137-144)
```rust
	/// Try to push an additional order.
	///
	/// Fails if queue is already at capacity.
	fn try_push(&mut self, now: N, para_id: ParaId) -> Result<(), ParaId> {
		self.queue
			.try_push(EnqueuedOrder { para_id, ordered_at: now })
			.map_err(|o| o.para_id)
	}
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L252-256)
```rust
	#[pallet::error]
	pub enum Error<T> {
		/// The order queue is full, `place_order` will not continue.
		QueueFull,
		/// The current spot price is higher than the max amount specified in the `place_order`
```
