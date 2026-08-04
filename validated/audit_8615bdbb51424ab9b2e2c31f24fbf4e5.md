### Title
Missing `para_id` validation in `do_place_order` allows queue-filling / spot-price griefing via `place_order_with_credits` - (File: polkadot/runtime/parachains/src/on_demand/mod.rs)

### Summary
`do_place_order` never verifies that `para_id` refers to a registered/onboarded parachain or parathread before charging the caller and pushing an `EnqueuedOrder` into `OrderQueue`. Any signed account holding a positive `Credits` balance can repeatedly call `place_order_with_credits` for an arbitrary, unregistered `ParaId`, filling the shared on-demand queue and inflating `spot_price` via `update_spot_traffic` with orders that can never be legitimately assigned or consumed.

### Finding Description
`do_place_order` computes `spot_price` from `order_status.traffic`, checks only `spot_price <= max_amount` and `order_status.queue.len() < on_demand_queue_max_size`, then charges the sender (via `Credits::<T>::insert`/`remove` for the `PaymentType::Credits` path) and unconditionally does `order_status.queue.try_push(now, para_id)`: [1](#0-0) 

There is no call to any `paras::Pallet::<T>` lookup (e.g. `is_parathread`, `is_valid_para`, membership in `paras::Parachains`/`ParaLifecycles`) anywhere in `do_place_order`, in the dispatchables `place_order_allow_death`/`place_order_keep_alive`/`place_order_with_credits`, or in the `Config` trait bound usage within this function — despite `Config: paras::Config` being available: [2](#0-1) 

`OrderQueue::try_push` and `pop_assignment_for_cores` also perform no `para_id` validity check; they operate purely on whatever `ParaId` value was supplied: [3](#0-2) 

Given the stated precondition that the attacker already possesses a positive `Credits` balance, the `PaymentType::Credits` branch only checks `credits.checked_sub(&spot_price)`, which succeeds as long as the attacker has enough credits for the current spot price — nothing here validates `para_id`: [4](#0-3) 

Because `update_spot_traffic` derives the new traffic/spot price purely from `order_status.queue.len()` versus `on_demand_queue_max_size` and `on_demand_target_queue_utilization` — with no distinction between orders for real vs. fake paras — pushing junk orders for a bogus `para_id` directly inflates the traffic multiplier and thus the price paid by legitimate on-demand purchasers: [5](#0-4) 

The queue is bounded (`ON_DEMAND_MAX_QUEUE_MAX_SIZE`, and further capped by `on_demand_queue_max_size` from `HostConfiguration`), so repeated calls with a fake `para_id` can occupy queue slots up to `on_demand_queue_max_size`, causing subsequent legitimate `place_order_*` calls (for real, valid paras) to fail with `Error::QueueFull`: [6](#0-5) [7](#0-6) 

The only mitigating factor is that stale/unassignable entries eventually leave the queue once popped by `pop_assignment_for_cores` (they are removed even if they never get assigned to a core, since the pop logic iterates and drops orders that are "ready" regardless of whether the scheduler can actually use the `ParaId`), which bounds this to a temporary — but repeatable and cheap (credits, not real currency in the worst case if credits are cheaply obtained) — griefing vector rather than a permanent full-halt. Still, within the scoped impact (temporary DoS via `QueueFull` and spot-price inflation for legitimate payers), this is exploitable purely through the public, unprivileged extrinsic `place_order_with_credits`.

### Impact Explanation
An attacker with any positive `Credits` balance can call `place_order_with_credits` in a loop targeting a `para_id` that is not a registered parachain/parathread, since `do_place_order` never validates `para_id` against `paras::Pallet::<T>`. This lets the attacker (a) occupy on-demand queue capacity with orders that can never be consumed by real coretime work, causing legitimate `place_order_*` calls to fail with `QueueFull`, and (b) drive up `traffic`/`spot_price` via `update_spot_traffic`, forcing genuine payers to pay inflated prices or be rejected by `SpotPriceHigherThanMaxAmount`. This is a DoS/griefing vector against the on-demand marketplace, not an asset-theft bug.

### Likelihood Explanation
Feasibility is high given the stated precondition (attacker already has positive `Credits`): the call path `ensure_signed(origin) -> do_place_order` is fully reachable via the public extrinsic `place_order_with_credits`, requires no special origin/proxy/multisig privilege, and can be repeated as many times as the attacker's credit balance and queue capacity (`on_demand_queue_max_size`, bounded by `ON_DEMAND_MAX_QUEUE_MAX_SIZE`) allow. The cost scales with the current `spot_price` in credits per order, and price will rise via `update_spot_traffic` as the queue fills, which bounds — but does not prevent — the attack.

### Recommendation
Add a validity check in `do_place_order` before charging and enqueueing, e.g. `ensure!(paras::Pallet::<T>::is_parachain(para_id) || paras::Pallet::<T>::is_parathread(para_id), Error::<T>::InvalidParaId);`, mirroring lifecycle checks used elsewhere in the scheduler/paras pallets, so only orders for currently onboarded paras can be placed and counted toward `spot_price`/`traffic`.

### Proof of Concept
Rust unit test in `polkadot/runtime/parachains/src/on_demand/tests.rs`:
1. Set up mock runtime with `Config: paras::Config`, do not register `para_id = ParaId::from(9999)` in `paras::Parachains`/`ParaLifecycles`.
2. Call `OnDemand::credit_account(attacker, small_amount)` (or via whatever public path grants credits in the test harness), then repeatedly call `OnDemand::place_order_with_credits(RuntimeOrigin::signed(attacker), BalanceOf::max_value(), ParaId::from(9999))`.
3. Assert each call succeeds (`Ok(())`) and emits `OnDemandOrderPlaced` despite `para_id` never being registered as a parachain/parathread — proving the missing `is_parathread`/`is_parachain` check.
4. Continue looping until `OnDemand::get_order_status().queue.len() == on_demand_queue_max_size`; assert the next call returns `Error::<T>::QueueFull`.
5. As a secondary assertion, call `place_order_with_credits` (or `place_order_allow_death`) from a second legitimate account for a real registered `para_id` and assert it also fails with `QueueFull`, proving legitimate orders are blocked by the attacker's fake-para orders, and assert `OnDemand::get_order_status().traffic` increased above `TrafficDefaultValue` purely due to the fake orders (spot-price manipulation).

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L100-104)
```rust
/// All queued on-demand orders.
#[derive(Encode, Decode, TypeInfo)]
pub struct OrderQueue<N> {
	queue: BoundedVec<EnqueuedOrder<N>, ConstU32<ON_DEMAND_MAX_QUEUE_MAX_SIZE>>,
}
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L108-144)
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

	fn new() -> Self {
		OrderQueue { queue: BoundedVec::new() }
	}

	/// Try to push an additional order.
	///
	/// Fails if queue is already at capacity.
	fn try_push(&mut self, now: N, para_id: ParaId) -> Result<(), ParaId> {
		self.queue
			.try_push(EnqueuedOrder { para_id, ordered_at: now })
			.map_err(|o| o.para_id)
	}
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L379-394)
```rust
		#[pallet::call_index(2)]
		#[pallet::weight(<T as Config>::WeightInfo::place_order_with_credits())]
		pub fn place_order_with_credits(
			origin: OriginFor<T>,
			max_amount: BalanceOf<T>,
			para_id: ParaId,
		) -> DispatchResult {
			let sender = ensure_signed(origin)?;
			Pallet::<T>::do_place_order(
				sender,
				max_amount,
				para_id,
				KeepAlive,
				PaymentType::Credits,
			)
		}
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L490-548)
```rust
			ensure!(spot_price.le(&max_amount), Error::<T>::SpotPriceHigherThanMaxAmount);

			ensure!(
				order_status.queue.len() <
					config.scheduler_params.on_demand_queue_max_size as usize,
				Error::<T>::QueueFull
			);

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

			let now = <frame_system::Pallet<T>>::block_number();
			order_status
				.queue
				.try_push(now, para_id)
				.defensive_map_err(|_| Error::<T>::QueueFull)?;
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L561-594)
```rust
	fn update_spot_traffic(
		config: &configuration::HostConfiguration<BlockNumberFor<T>>,
		order_status: &mut OrderStatus<BlockNumberFor<T>>,
	) {
		let old_traffic = order_status.traffic;
		match Self::calculate_spot_traffic(
			old_traffic,
			config.scheduler_params.on_demand_queue_max_size,
			order_status.queue.len() as u32,
			config.scheduler_params.on_demand_target_queue_utilization,
			config.scheduler_params.on_demand_fee_variability,
		) {
			Ok(new_traffic) => {
				// Only update storage on change
				if new_traffic != old_traffic {
					order_status.traffic = new_traffic;

					// calculate the new spot price
					let spot_price: BalanceOf<T> = new_traffic.saturating_mul_int(
						config.scheduler_params.on_demand_base_fee.saturated_into::<BalanceOf<T>>(),
					);

					// emit the event for updated new price
					Pallet::<T>::deposit_event(Event::<T>::SpotPriceSet { spot_price });
				}
			},
			Err(err) => {
				log::debug!(
					target: LOG_TARGET,
					"Error calculating spot traffic: {:?}", err
				);
			},
		};
	}
```
