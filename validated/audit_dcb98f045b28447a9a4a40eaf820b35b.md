### Title
Single actor can monopolize the shared on-demand order queue via fee-priced spam, causing `Error::QueueFull` for legitimate on-demand paras - (File: polkadot/runtime/parachains/src/on_demand/mod.rs)

### Summary
The on-demand queue (`OrderStatus.queue`) is a single global `BoundedVec` shared by all `ParaId`s, with no per-para reservation, quota, or rate limit. An attacker with enough balance/credits can repeatedly call `place_order_allow_death`/`place_order_with_credits` for one `para_id` to fill the queue up to `on_demand_queue_max_size`, and the only defense (the `traffic`/`spot_price` escalation in `calculate_spot_traffic`) is a *global* congestion-pricing mechanism, not a per-actor or per-para fairness mechanism.

### Finding Description
`do_place_order` (polkadot/runtime/parachains/src/on_demand/mod.rs:471-558) charges `spot_price` and then unconditionally pushes `(now, para_id)` into the single shared `order_status.queue` via `OrderQueue::try_push` (mod.rs:140-144), rejecting only when `order_status.queue.len() >= on_demand_queue_max_size` (mod.rs:492-496). There is no check limiting how many of the currently-queued entries belong to the same `para_id`, nor any check on how many entries a single `sender` account has enqueued. This is explicitly documented as a single shared queue design (mod.rs:22-27): "The module uses a single queue for all on-demand orders... only one order per ParaId can be assigned in each scheduling round" — this constraint only affects *assignment* (`pop_assignment_for_cores`, mod.rs:108-131, which dedupes per para per round via a `BTreeSet`), not *enqueuing*. So an attacker paying the fee can enqueue many entries for the same `para_id`, filling the bounded queue, while legitimate other paras' orders get `Error::QueueFull`.

The only cost-based mitigation is `update_spot_traffic`/`calculate_spot_traffic` (mod.rs:560-665), which raises `traffic` (and thus `spot_price`) as `queue_size/queue_capacity` exceeds `on_demand_target_queue_utilisation`. This is a *global* traffic multiplier tied to overall queue occupancy, not tied to per-para or per-account share — it makes filling the queue progressively more expensive for everyone equally, but does not prevent one well-funded actor from paying the escalating price to occupy the entire queue, since each successive `try_push` for the same para is treated identically to any other legitimate order.

### Impact Explanation
If an attacker with sufficient balance/credits fills the shared queue to `on_demand_queue_max_size` with orders for a single low-value `para_id`, every other account attempting `place_order_allow_death`/`place_order_with_credits`/`place_order_keep_alive` for *any other* `para_id` receives `Error::QueueFull` (mod.rs:492-496) until the attacker's orders are popped off by `pop_assignment_for_cores` (bounded by available on-demand cores per block) or the attacker stops. This is a relay-chain-wide denial of on-demand blockspace access for all other parachains during that window — matching the scoped impact.

### Likelihood Explanation
Feasibility depends entirely on the attacker's capital relative to the fee-escalation curve. Since `calculate_spot_traffic` increases `traffic` monotonically with queue utilization and has no upper bound other than `FixedU128::MAX`, the *cost* to fully saturate the queue in one block is bounded but can be arbitrarily large depending on `on_demand_fee_variability`/`on_demand_target_queue_utilization` configured for the chain — this is an economic parameter, not a hard protocol invariant. The attack is trivially reachable via ordinary signed extrinsics (no privileged origin needed), and is repeatable every block as attacker replenishes queue slots that get consumed by scheduling. Whether this constitutes a "bug" versus intended economic design (queue access is meant to be a first-come, fee-priced-first-served market, similar to fee markets elsewhere in Substrate/Ethereum) is the central question — the code and docs indicate this is the intended mechanism (congestion pricing rather than fixed per-actor quotas), so griefing is only economically rational/sustainable if the fee curve is misconfigured to grow too slowly relative to the attacker's budget. This is a parameterization/tuning risk rather than a missing-check logic bug in `do_place_order` itself.

### Recommendation
If stronger fairness guarantees than pure fee-based congestion pricing are desired, consider adding an explicit per-`ParaId` or per-account cap on outstanding queue entries (e.g., reject new orders for a `para_id` that already has N entries pending), independent of `traffic`/`spot_price`, so that no single para/account can occupy more than a bounded fraction of `on_demand_queue_max_size` regardless of funding. Alternatively, document and audit that `on_demand_fee_variability`/`on_demand_target_queue_utilization`/`on_demand_base_fee` are tuned such that queue-filling cost grows fast enough to bound worst-case monopolization duration to an acceptable value, and expose tooling/tests validating that assumption for each configured relay chain.

### Proof of Concept
Rust unit/integration test extending `polkadot/runtime/parachains/src/on_demand/tests.rs`:
```
1. Set on_demand_queue_max_size = N (small, e.g. 20) via test config/`configuration::ActiveConfig`.
2. Fund `attacker` with a very large balance.
3. Register two paras: `attacker_para` and `victim_para`.
4. Loop calling `OnDemand::place_order_allow_death(attacker, max_amount=u128::MAX, attacker_para)`
   N times in the same block, asserting each `Ok(())` and that `OnDemand::get_order_status().queue.len()` increments,
   and recording the spot_price paid each iteration (should increase per `SpotPriceSet` events).
5. Assert queue is now full: `OnDemand::get_order_status().queue.len() == N`.
6. Fund `victim` with sufficient balance and call
   `OnDemand::place_order_allow_death(victim, max_amount, victim_para)`,
   assert it returns `Err(Error::<Test>::QueueFull)`.
7. (Fuzz/invariant extension) Parametrize N, `on_demand_fee_variability`, `on_demand_target_queue_utilization`,
   and attacker budget; assert whether attacker's total spend to reach full saturation stays below a
   configurable "safety threshold" — flag configurations where it does not, to validate/tune the economic parameters.
```
This confirms the shared-queue fill and the resulting `QueueFull` denial for a legitimate other para, while leaving open (for chain governance to tune) whether the fee-escalation curve bounds the economic feasibility below an acceptable griefing budget. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L22-27)
```rust
//!
//! The module uses a single queue for all on-demand orders. Orders are generally processed in the
//! order they are received, but with an important constraint: only one order per ParaId can be
//! assigned in each scheduling round. If multiple orders for the same ParaId exist in the queue,
//! only the first will be assigned, and subsequent orders for that ParaId will remain queued until
//! the next round.
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L100-149)
```rust
/// All queued on-demand orders.
#[derive(Encode, Decode, TypeInfo)]
pub struct OrderQueue<N> {
	queue: BoundedVec<EnqueuedOrder<N>, ConstU32<ON_DEMAND_MAX_QUEUE_MAX_SIZE>>,
}

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

	fn len(&self) -> usize {
		self.queue.len()
	}
}
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L471-558)
```rust
	fn do_place_order(
		sender: <T as frame_system::Config>::AccountId,
		max_amount: BalanceOf<T>,
		para_id: ParaId,
		existence_requirement: ExistenceRequirement,
		payment_type: PaymentType,
	) -> DispatchResult {
		let config = configuration::ActiveConfig::<T>::get();

		pallet::OrderStatus::<T>::mutate(|order_status| {
			Self::update_spot_traffic(&config, order_status);
			let traffic = order_status.traffic;

			// Calculate spot price
			let spot_price: BalanceOf<T> = traffic.saturating_mul_int(
				config.scheduler_params.on_demand_base_fee.saturated_into::<BalanceOf<T>>(),
			);

			// Is the current price higher than `max_amount`
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

			Pallet::<T>::deposit_event(Event::<T>::OnDemandOrderPlaced {
				para_id,
				spot_price,
				ordered_by: sender,
			});

			Ok(())
		})
	}
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L560-665)
```rust
	/// Calculate and update spot traffic.
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

	/// The spot price multiplier. This is based on the transaction fee calculations defined in:
	/// https://research.web3.foundation/Polkadot/overview/token-economics#setting-transaction-fees
	///
	/// Parameters:
	/// - `traffic`: The previously calculated multiplier, can never go below 1.0.
	/// - `queue_capacity`: The max size of the order book.
	/// - `queue_size`: How many orders are currently in the order book.
	/// - `target_queue_utilisation`: How much of the queue_capacity should be ideally occupied,
	///   expressed in percentages(perbill).
	/// - `variability`: A variability factor, i.e. how quickly the spot price adjusts. This number
	///   can be chosen by p/(k*(1-s)) where p is the desired ratio increase in spot price over k
	///   number of blocks. s is the target_queue_utilisation. A concrete example: v =
	///   0.05/(20*(1-0.25)) = 0.0033.
	///
	/// Returns:
	/// - A `FixedU128` in the range of  `Config::TrafficDefaultValue` - `FixedU128::MAX` on
	///   success.
	///
	/// Errors:
	/// - `SpotTrafficCalculationErr::QueueCapacityIsZero`
	/// - `SpotTrafficCalculationErr::QueueSizeLargerThanCapacity`
	/// - `SpotTrafficCalculationErr::Division`
	fn calculate_spot_traffic(
		traffic: FixedU128,
		queue_capacity: u32,
		queue_size: u32,
		target_queue_utilisation: Perbill,
		variability: Perbill,
	) -> Result<FixedU128, SpotTrafficCalculationErr> {
		// Return early if queue has no capacity.
		if queue_capacity == 0 {
			return Err(SpotTrafficCalculationErr::QueueCapacityIsZero);
		}

		// Return early if queue size is greater than capacity.
		if queue_size > queue_capacity {
			return Err(SpotTrafficCalculationErr::QueueSizeLargerThanCapacity);
		}

		// (queue_size / queue_capacity) - target_queue_utilisation
		let queue_util_ratio = FixedU128::from_rational(queue_size.into(), queue_capacity.into());
		let positive = queue_util_ratio >= target_queue_utilisation.into();
		let queue_util_diff = queue_util_ratio.max(target_queue_utilisation.into()) -
			queue_util_ratio.min(target_queue_utilisation.into());

		// variability * queue_util_diff
		let var_times_qud = queue_util_diff.saturating_mul(variability.into());

		// variability^2 * queue_util_diff^2
		let var_times_qud_pow = var_times_qud.saturating_mul(var_times_qud);

		// (variability^2 * queue_util_diff^2)/2
		let div_by_two: FixedU128;
		match var_times_qud_pow.const_checked_div(2.into()) {
			Some(dbt) => div_by_two = dbt,
			None => return Err(SpotTrafficCalculationErr::Division),
		}

		// traffic * (1 + queue_util_diff) + div_by_two
		if positive {
			let new_traffic = queue_util_diff
				.saturating_add(div_by_two)
				.saturating_add(One::one())
				.saturating_mul(traffic);
			Ok(new_traffic.max(<T as Config>::TrafficDefaultValue::get()))
		} else {
			let new_traffic = queue_util_diff.saturating_sub(div_by_two).saturating_mul(traffic);
			Ok(new_traffic.max(<T as Config>::TrafficDefaultValue::get()))
		}
	}
```
