Confirmed: `do_place_order` in `polkadot/runtime/parachains/src/on_demand/mod.rs` never validates that `para_id` is a registered parathread before charging and enqueuing the order.I have enough evidence to render a verdict now.### Title
Missing parathread validation in `do_place_order` allows unprivileged spot-price/queue griefing via orders for non-existent or non-parathread `para_id`s - (File: polkadot/runtime/parachains/src/on_demand/mod.rs)

### Summary
`do_place_order` charges the caller (in `Balance` or `Credits`) and pushes into `OrderStatus::queue` for any `ParaId` supplied by the caller, without ever verifying `paras::Pallet::<T>::is_parathread(para_id)` (or `is_parachain`). This lets any signed account with credits or funds place spot-priced on-demand orders for arbitrary/unregistered `para_id`s, inflating `order_status.queue.len()` (driving up `traffic`/`spot_price` via `update_spot_traffic`) and consuming queue capacity up to `on_demand_queue_max_size`, degrading service and pricing for legitimate on-demand users.

### Finding Description
`place_order_with_credits`, `place_order_allow_death`, and `place_order_keep_alive` all call `ensure_signed(origin)` and then `Pallet::<T>::do_place_order(sender, max_amount, para_id, ..)` with a caller-supplied `para_id` [1](#0-0) . In `do_place_order`, the function computes `spot_price` from `traffic`, checks `spot_price <= max_amount` and `queue.len() < on_demand_queue_max_size`, deducts the price (via `Currency::withdraw` for `PaymentType::Balance` or by decrementing `Credits::<T>` for `PaymentType::Credits`), and finally does `order_status.queue.try_push(now, para_id)` [2](#0-1) . At no point is `paras::Pallet::<T>::is_parathread(para_id)` or `is_parachain(para_id)` checked — there is no such call anywhere in this function.

Because `update_spot_traffic` recalculates `traffic` (and thus `spot_price`) purely as a function of `order_status.queue.len()` relative to `on_demand_queue_max_size` and `on_demand_target_queue_utilization` [3](#0-2) , any queue entries — even for nonexistent/non-parathread `para_id`s — count toward driving traffic/spot price up just like genuine orders.

`place_order_with_credits` only requires `ensure_signed` and a positive `Credits::<T>` balance, both of which are attacker-controllable (an attacker can acquire a small legitimate credit via `credit_account`, which is invoked from elsewhere in the runtime as part of normal, non-privileged flows, or simply via `place_order_allow_death`/`place_order_keep_alive` with real balance). The attacker then repeatedly calls `place_order_with_credits(fake_para_id, max_amount = BalanceOf::<T>::max_value())` for a `para_id` that is not a valid parathread. Each call succeeds (subject only to price/queue-size checks, not para validity), pushing junk entries into `OrderQueue` until `QueueFull` is hit.

Downstream, `pop_assignment_for_cores`/`advance_assignments` in the scheduler's coretime assigner consume entries from this queue purely by `ParaId` without re-validating parathread status before scheduling [4](#0-3) ; a fake/unregistered `para_id` occupies a core assignment slot that will never be "consumed" by an actual candidate, effectively wasting coretime scheduling capacity as well as queue capacity.

### Impact Explanation
This is a denial-of-service and economic griefing vector against the on-demand market:
- **Queue exhaustion (`QueueFull` griefing):** attacker fills `OrderQueue` up to `on_demand_queue_max_size` with orders for a para that can never produce a valid candidate, causing legitimate `place_order_*` calls (for real parathreads) to fail with `Error::QueueFull`.
- **Spot-price manipulation:** since `update_spot_traffic`/`calculate_spot_traffic` scale `traffic` (and hence `spot_price`) with `queue.len()` relative to `on_demand_queue_max_size`, injecting junk orders artificially inflates the traffic multiplier, forcing genuine payers to pay a higher spot price than organic demand would justify.
- **Wasted coretime scheduling slots:** downstream schedulers pop these bogus assignments for actual cores, wasting core-time that could have gone to real parachains.

The attacker's own funds/credits are spent to do this, but the amount required is bounded by `spot_price` (which starts low and only rises with traffic), not by `max_amount = BalanceOf::<T>::max_value()` — so the cost to grief is the accumulated spot price of enough orders to fill the queue, not the attacker's `max_amount` parameter (which is merely a "will not pay more than X" ceiling).

### Likelihood Explanation
Preconditions are trivial for any unprivileged account: a signed origin and any positive `Credits::<T>` balance (or free balance for the deprecated `Balance` variants). No proxy, multisig, XCM, or privileged access is required — a straightforward loop of `place_order_with_credits` extrinsics with an arbitrary/unregistered `ParaId` is directly reachable and repeatable up to `on_demand_queue_max_size` (bounded by `ON_DEMAND_MAX_QUEUE_MAX_SIZE`) per griefing round.

### Recommendation
In `do_place_order`, add an early validation such as:
```rust
ensure!(paras::Pallet::<T>::is_parathread(para_id) || paras::Pallet::<T>::is_parachain(para_id), Error::<T>::InvalidParaId);
```
before charging the sender and pushing into `order_status.queue`, mirroring the pattern already used elsewhere in the codebase (e.g., `Registrar::make_parachain`/`make_parathread` checks against `paras::Pallet::<T>::lifecycle`) [5](#0-4) .

### Proof of Concept
Add to `polkadot/runtime/parachains/src/on_demand/tests.rs`:
```rust
#[test]
fn place_order_for_non_parathread_para_should_fail_but_currently_succeeds() {
    let alice = 1u64;
    let fake_para_id = ParaId::from(9999); // never registered/scheduled as parathread or parachain

    new_test_ext(GenesisConfigBuilder::default().build()).execute_with(|| {
        OnDemand::credit_account(alice, 10_000_000u128);
        assert!(!Paras::is_parathread(fake_para_id));
        assert!(!Paras::is_parachain(fake_para_id));

        // BUG: this currently succeeds despite fake_para_id never being a valid para.
        assert_ok!(OnDemand::place_order_with_credits(
            RuntimeOrigin::signed(alice),
            10_000_000u128,
            fake_para_id
        ));

        // Fill queue to max with fake_para_id orders, then show legitimate order for a
        // real parathread fails with QueueFull.
        let config = configuration::ActiveConfig::<Test>::get();
        let max_size = config.scheduler_params.on_demand_queue_max_size as usize;
        OnDemand::credit_account(alice, 1_000_000_000_000u128);
        for _ in 1..max_size {
            let _ = OnDemand::place_order_with_credits(
                RuntimeOrigin::signed(alice),
                1_000_000_000_000u128,
                fake_para_id,
            );
        }

        let real_para_id = ParaId::from(111);
        schedule_blank_para(real_para_id, ParaKind::Parathread);
        run_to_block(100, |n| if n == 100 { Some(Default::default()) } else { None });
        OnDemand::credit_account(alice, 1_000_000_000_000u128);

        assert_noop!(
            OnDemand::place_order_with_credits(
                RuntimeOrigin::signed(alice),
                1_000_000_000_000u128,
                real_para_id
            ),
            Error::<Test>::QueueFull
        );
    });
}
```
Expected assertions: the first `place_order_with_credits` call for an unregistered `para_id` succeeds (proving the missing validation), the queue fills entirely with bogus orders, and a subsequent legitimate order for a real registered parathread fails with `Error::<Test>::QueueFull`, demonstrating the DoS/griefing impact.

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L381-394)
```rust
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

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L480-548)
```rust
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
```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L560-593)
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
```

**File:** polkadot/runtime/parachains/src/scheduler/assigner_coretime/mod.rs (L385-426)
```rust
pub(super) fn advance_assignments<T: Config, F: Fn(CoreIndex) -> bool>(
	is_blocked: F,
) -> BTreeMap<CoreIndex, ParaId> {
	let now = frame_system::Pallet::<T>::block_number();

	let assignments = super::CoreDescriptors::<T>::mutate(|core_states| {
		advance_assignments_single_impl::<T>(now, core_states, AccessMode::<T>::pop())
	});

	// Give blocked on-demand orders another chance:
	for blocked in assignments.pool_assignments.iter().filter_map(|(core_idx, para_id)| {
		if is_blocked(*core_idx) {
			Some(*para_id)
		} else {
			None
		}
	}) {
		on_demand::Pallet::<T>::push_back_order(blocked);
	}

	let mut assignments: BTreeMap<CoreIndex, ParaId> =
		assignments.into_iter().filter(|(core_idx, _)| !is_blocked(*core_idx)).collect();

	// Try to fill missing assignments from the next position (duplication to allow asynchronous
	// backing even for first assignment coming in on a previously empty core):
	let next = now.saturating_plus_one();
	let mut core_states = super::CoreDescriptors::<T>::get();
	let mut on_demand_orders = on_demand::Pallet::<T>::peek_order_queue();
	let next_assignments = advance_assignments_single_impl(
		next,
		&mut core_states,
		AccessMode::<T>::peek(&mut on_demand_orders),
	)
	.into_iter();

	for (core_idx, next_assignment) in
		next_assignments.filter(|(core_idx, _)| !is_blocked(*core_idx))
	{
		assignments.entry(core_idx).or_insert_with(|| next_assignment);
	}
	assignments
}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L521-532)
```rust
	// Upgrade a registered on-demand parachain into a lease holding parachain.
	fn make_parachain(id: ParaId) -> DispatchResult {
		// Para backend should think this is an on-demand parachain...
		ensure!(
			paras::Pallet::<T>::lifecycle(id) == Some(ParaLifecycle::Parathread),
			Error::<T>::NotParathread
		);
		polkadot_runtime_parachains::schedule_parathread_upgrade::<T>(id)
			.map_err(|_| Error::<T>::CannotUpgrade)?;

		Ok(())
	}
```
