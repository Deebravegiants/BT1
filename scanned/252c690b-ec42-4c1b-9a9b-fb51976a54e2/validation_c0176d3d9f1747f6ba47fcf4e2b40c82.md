### Title
`do_place_order` allows unprivileged users to pay for on-demand orders targeting invalid/offboarded `para_id`s with no possibility of ever being usefully scheduled - ([File: polkadot/runtime/parachains/src/on_demand/mod.rs])

### Summary
`Pallet::do_place_order` withdraws the spot price (or burns credits) and enqueues an order for any `ParaId` supplied by the caller, without checking that the `para_id` corresponds to a currently valid parathread/parachain. Since `paras::Pallet::<T>::is_valid_para` is trivially reachable (the pallet's `Config: paras::Config`), but is never called, a signed user can place — and pay for — an order for a `para_id` that is unregistered, still onboarding, or already scheduled for/undergoing offboarding, permanently losing funds for an assignment that can never back a real candidate.

### Finding Description
`do_place_order` at [1](#0-0)  only validates the spot price against `max_amount` and checks queue capacity before charging the sender: [2](#0-1)  then unconditionally withdraws balance or burns credits, credits `Revenue::<T>` for the current block, and pushes `(para_id, now)` into the on-demand `OrderQueue` — none of these steps consult `paras::Pallet::<T>::is_valid_para(para_id)` (defined at [3](#0-2) ) even though `Config: paras::Config` makes this check trivially available.

Downstream, `OrderQueue::pop_assignment_for_cores` at [4](#0-3)  selects ready orders purely by `ordered_at`/`ready_at` and de-duplicates by `para_id` — it performs no liveness/validity check against the `paras` pallet either. The popped `para_id` is fed into the coretime assigner (`assigner_coretime::advance_assignments_single_impl` / `pop_assignment_for_ondemand_cores`, [5](#0-4) ), which likewise does not filter by para validity before turning the pool slot into a `CoreAssignment::Task(para_id)`.

Because a para that is unregistered or offboarded cannot back any candidate on that core, the assignment is effectively wasted — the funds were already withdrawn/burned and `Revenue` already incremented at order-placement time, well before scheduling occurs, and there is no refund or rejection path for orders that later prove unschedulable.

Attacker flow:
1. Attacker (any signed account) calls `place_order_allow_death`/`place_order_keep_alive`/`place_order_with_credits` with a `para_id` that is not currently `is_valid_para` (never registered, still `Onboarding`, or already `OffboardingParathread`/`OffboardingParachain`).
2. `do_place_order` withdraws `spot_price` from the attacker's own balance/credits (self-inflicted loss, but demonstrates the missing validation exists in the same way it would for third-party griefing scenarios, e.g. placing orders that drain the shared queue slot for a para that will never occupy a core), increments `Revenue::<T>`, and pushes the order into the queue — all unconditionally.
3. Several blocks later, `pop_assignment_for_cores`/the coretime assigner pops this order and "assigns" the para to a core, but since the para doesn't exist/is being torn down, no valid candidate can ever be backed with it — the on-demand core cycle for that slot is wasted and the funds are permanently gone into the pallet's revenue pot.

### Impact Explanation
The unprivileged caller's funds (native balance withdrawal or on-demand credits) are irreversibly consumed for an order that cannot result in any block production, and `Revenue::<T>` (destined for teleport to the Coretime chain) is credited for value that produced no service — a direct instance of "burn assets for an operation that cannot execute." This also wastes a slot in the shared, capacity-bounded `OrderQueue`, degrading availability for legitimate orders queued at the same time.

### Likelihood Explanation
Highly likely to occur naturally (not even requiring malice): a user can legitimately place an order and, before the 2-block async-backing delay elapses, the target para can be deregistered/offboarded via `paras_registrar` or a runtime upgrade path chosen by its own collators/sudo, or a user can simply typo/target a still-onboarding or never-registered `ParaId`. `do_place_order` never rejects such input, so the loss is deterministic and 100% reproducible given the precondition (`is_valid_para(para_id) == false` at call time or shortly after).

### Recommendation
Add an explicit `ensure!(<paras::Pallet<T>>::is_valid_para(para_id), Error::<T>::InvalidParaId)` (or an equivalent liveness check appropriate for on-demand, e.g. requiring `ParaLifecycle::is_parathread`/`is_parachain` and not `is_offboarding`) at the start of `do_place_order`, before any funds are withdrawn or `Revenue`/queue mutations occur. Consider also re-validating (or dropping stale) orders in `pop_assignment_for_cores` for paras that transitioned to offboarding while queued, refunding or re-queuing as appropriate.

### Proof of Concept
Rust unit test in `polkadot/runtime/parachains/src/on_demand/tests.rs`:
1. Set up test externalities without registering `para_id = ParaId::from(999)` (or register it and then call the registrar/paras pallet's offboarding path and run to the session where `ParaLifecycles::<Test>::get(para_id)` becomes `None`/`OffboardingParathread`).
2. Assert `Paras::is_valid_para(para_id) == false`.
3. Call `OnDemand::place_order_allow_death(RuntimeOrigin::signed(attacker), max_amount, para_id)` and assert it currently returns `Ok(())` (demonstrating the missing check) while `Balances::free_balance(attacker)` decreases by `spot_price` and `OnDemand::get_revenue()` increases by `spot_price`.
4. Advance blocks and call `OnDemand::pop_assignment_for_cores(block_num, num_cores)`; assert the popped iterator yields `para_id` even though `Paras::is_valid_para(para_id) == false`, proving the assignment can never back a real candidate.
5. Assert no compensating refund occurred: `Balances::free_balance(attacker)` remains reduced and `Revenue::<Test>::get()` remains incremented, confirming permanent fund loss for a scheduling-impossible order.

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

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L471-497)
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

```

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L498-548)
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

			let now = <frame_system::Pallet<T>>::block_number();
			order_status
				.queue
				.try_push(now, para_id)
				.defensive_map_err(|_| Error::<T>::QueueFull)?;
```

**File:** polkadot/runtime/parachains/src/paras/mod.rs (L2462-2471)
```rust
	/// Returns whether the given ID refers to a valid para.
	///
	/// Paras that are onboarding or offboarding are not included.
	pub fn is_valid_para(id: ParaId) -> bool {
		if let Some(state) = ParaLifecycles::<T>::get(&id) {
			!state.is_onboarding() && !state.is_offboarding()
		} else {
			false
		}
	}
```

**File:** polkadot/runtime/parachains/src/scheduler/assigner_coretime/mod.rs (L279-294)
```rust
	/// Pop pool assignments according to access mode.
	fn pop_assignment_for_ondemand_cores(
		&mut self,
		now: BlockNumberFor<T>,
		num_cores: u32,
	) -> impl Iterator<Item = ParaId> {
		match self {
			Self::Peek { on_demand_orders } => on_demand_orders
				.pop_assignment_for_cores::<T>(now, num_cores)
				.collect::<Vec<_>>(),
			Self::Pop => {
				on_demand::Pallet::<T>::pop_assignment_for_cores(now, num_cores).collect::<Vec<_>>()
			},
		}
		.into_iter()
	}
```
