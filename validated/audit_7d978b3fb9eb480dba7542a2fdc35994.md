### Title
Unprivileged callers can burn funds/credits via `do_place_order` for a `para_id` that is not a valid on-demand parathread, with `Revenue` incremented regardless - ([File: polkadot/runtime/parachains/src/on_demand/mod.rs])

### Summary
`Pallet::do_place_order` withdraws the spot price (or burns credits) and pushes the order into the on-demand queue without ever validating that `para_id` refers to a currently registered/onboarded on-demand parathread. `Pallet::pop_assignment_for_cores` (and the inner `OrderQueue::pop_assignment_for_cores`) likewise perform no validity check when popping orders for scheduling, so an order for a bogus or offboarded `para_id` is accepted, charged, and accounted into `Revenue`, even though it can never result in a real parachain-block assignment.

### Finding Description
`do_place_order` (`polkadot/runtime/parachains/src/on_demand/mod.rs:471-558`) is reachable by any signed account through the public extrinsics `place_order_allow_death`, `place_order_keep_alive`, and `place_order_with_credits` (lines 313-394), each of which does nothing but `ensure_signed(origin)` and forward the caller-supplied `para_id` straight into `do_place_order`.

Inside `do_place_order`, the checks performed are:
- `spot_price.le(&max_amount)` (price cap check),
- `order_status.queue.len() < on_demand_queue_max_size` (queue capacity check). [1](#0-0) 

There is no call to `paras::Pallet::<T>::is_parathread`, `is_valid_para`, or any lifecycle/registration check on `para_id` anywhere in this function before the funds are withdrawn (`T::Currency::withdraw`) or credits are debited (`Credits::<T>::insert`), and before `Revenue` is incremented: [2](#0-1) 

The order is then pushed into the queue unconditionally: [3](#0-2) 

On the scheduling side, `Pallet::pop_assignment_for_cores` simply delegates to `OrderQueue::pop_assignment_for_cores`, which pops ready orders purely based on `ordered_at`/`now` timing and a `BTreeSet` de-duplication by `para_id` — again with no check that `para_id` is a live parathread: [4](#0-3) [5](#0-4) 

I was unable to locate a separate `assigner_on_demand` module or scheduler-side `is_parathread`/`ParaLifecycle` gating logic in this checkout that consumes the output of `pop_assignment_for_cores` and could reject/re-queue an assignment for a since-offboarded para — my searches for `is_parathread`/`lifecycle`/`ParaLifecycle` under `polkadot/runtime/parachains/src/scheduler/` and for the on-demand assignment provider returned no results, so I could not confirm whether a downstream re-validation exists that would at least prevent silent loss of the core slot. This is a gap in my analysis that a background agent with full repo access should verify (the on-demand assignment provider code may exist elsewhere or under a different name/version in this checkout).

Given what is confirmed in `mod.rs`: `Revenue` accounting (line 533-542) happens purely as a function of order placement, decoupled from whether the order is ever actually turned into a scheduled/assigned core. So even if downstream logic discards an assignment for an invalid `para_id` (wasting the core), the caller's payment is already irreversibly consumed and already recorded in `Revenue` for payout to the Coretime chain — there is no refund path in this file.

### Impact Explanation
An unprivileged user can pay real balance or spend on-demand credits for a `para_id` that is not a valid/onboarded on-demand parathread (e.g., never registered, or offboarded between order placement and the 2-block-later scheduling window). The funds are withdrawn/credits burned and folded into `Revenue` at order-placement time regardless of eventual scheduling outcome, so if there is no downstream validity check (which I could not locate in this codebase), the payment is permanently lost and a core-slot is potentially wasted, satisfying "a user burns assets for an operation that cannot execute."

### Likelihood Explanation
Trivially reachable by any signed account calling `place_order_with_credits`/`place_order_allow_death`/`place_order_keep_alive` with an arbitrary `ParaId` (e.g., mistyped, deregistered, or offboarded). No special privileges, race conditions beyond ordinary offboarding timing, or non-standard setup are required — offboarding a parachain/parathread and losing pending on-demand orders is a normal chain-lifecycle event, not an edge case.

### Recommendation
Add a validity check in `do_place_order` before charging the user, e.g. `ensure!(<paras::Pallet<T>>::is_parathread(para_id), Error::<T>::InvalidParaId)` (or equivalent "para is onboarded and on-demand-eligible" check), and/or add the same check at the point of `pop_assignment_for_cores` to drop/refund orders for paras that were offboarded after order placement, ensuring `Revenue` is not credited for orders that cannot be fulfilled.

### Proof of Concept
Rust unit test in `polkadot/runtime/parachains/src/on_demand/tests.rs`:
1. Set up the on-demand pallet mock without registering `para_id` (or register then offboard it) so that `paras::Pallet::<Test>::is_parathread(para_id)` is `false`.
2. Call `OnDemand::place_order_with_credits(RuntimeOrigin::signed(caller), max_amount, para_id)` (after crediting `caller` via `credit_account`).
3. Assert the call succeeds (`Ok(())`) — demonstrating no rejection — and `Credits::<Test>::get(&caller)` decreased by `spot_price`.
4. Assert `Revenue::<Test>::get()[0]` increased by `spot_price`.
5. Advance blocks past the 2-block readiness window and call `OnDemand::pop_assignment_for_cores(now, num_cores)`; assert it returns `para_id` in spite of it being invalid, or (if a fix is applied) assert the order is dropped/refunded and `Revenue` is not incremented for it.
6. Add an assertion comparing `Revenue::<Test>::get()` total against the count of actually-assignable (valid-para) orders to expose the discrepancy.

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L108-131)
```rust
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

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L404-411)
```rust
	pub fn pop_assignment_for_cores(
		now: BlockNumberFor<T>,
		num_cores: u32,
	) -> impl Iterator<Item = ParaId> {
		pallet::OrderStatus::<T>::mutate(|order_status| {
			order_status.queue.pop_assignment_for_cores::<T>(now, num_cores)
		})
	}
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L489-496)
```rust
			// Is the current price higher than `max_amount`
			ensure!(spot_price.le(&max_amount), Error::<T>::SpotPriceHigherThanMaxAmount);

			ensure!(
				order_status.queue.len() <
					config.scheduler_params.on_demand_queue_max_size as usize,
				Error::<T>::QueueFull
			);
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L498-542)
```rust
			match payment_type {
				PaymentType::Balance => {
					// Charge the sending account the spot price. The amount will be teleported to
					// the broker chain once it requests revenue information.
					let amt = T::Currency::withdraw(
						&sender,
						spot_price,
						WithdrawReasons::FEE,
						existence_requirement,
					)?;

					// Consume the negative imbalance and deposit it into the pallet account. Make
					// sure the account preserves even without the existential deposit.
					let pot = Self::account_id();
					if !System::<T>::account_exists(&pot) {
						System::<T>::inc_providers(&pot);
					}
					T::Currency::resolve_creating(&pot, amt);
				},
				PaymentType::Credits => {
					let credits = Credits::<T>::get(&sender);

					// Charge the sending account the spot price in credits.
					let new_credits_value =
						credits.checked_sub(&spot_price).ok_or(Error::<T>::InsufficientCredits)?;

					if new_credits_value.is_zero() {
						Credits::<T>::remove(&sender);
					} else {
						Credits::<T>::insert(&sender, new_credits_value);
					}
				},
			}

			// Add the amount to the current block's (index 0) revenue information.
			Revenue::<T>::mutate(|bounded_revenue| {
				if let Some(current_block) = bounded_revenue.get_mut(0) {
					*current_block = current_block.saturating_add(spot_price);
				} else {
					// Revenue has already been claimed in the same block, including the block
					// itself. It shouldn't normally happen as revenue claims in the future are
					// not allowed.
					bounded_revenue.try_push(spot_price).defensive_ok();
				}
			});
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L544-548)
```rust
			let now = <frame_system::Pallet<T>>::block_number();
			order_status
				.queue
				.try_push(now, para_id)
				.defensive_map_err(|_| Error::<T>::QueueFull)?;
```
