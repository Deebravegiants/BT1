### Title
Unprivileged callers can burn funds/credits via `place_order_*` for a `para_id` that is not (or no longer) a valid on-demand parathread - (File: `polkadot/runtime/parachains/src/on_demand/mod.rs`)

### Summary
`Pallet::do_place_order` withdraws the spot price (balance or credits), credits `Revenue`, and pushes the order into the on-demand queue without ever verifying that `para_id` is a live, valid parathread via `paras::Pallet::is_parathread`. Since neither `do_place_order` nor the consuming code path (`pop_assignment_for_cores`, `advance_assignments_single_impl`) filters non-existent or offboarded `para_id`s, an order for such a `para_id` is charged and accounted as revenue even though it can never result in a produced block.

### Finding Description
`do_place_order` at [1](#0-0)  only validates `spot_price <= max_amount` and that the queue is not full — there is no call to `paras::Pallet::<T>::is_parathread(para_id)` or any other existence/validity check on `para_id` before charging the caller. The charge (via `Currency::withdraw` for balance payment, or `Credits` debit for credit payment) and the `Revenue` accumulation both happen unconditionally: [2](#0-1) . The order is then pushed into the queue purely by `ParaId` value with no further validation: [3](#0-2) .

Downstream, `OrderQueue::pop_assignment_for_cores` (used both directly and via `Pallet::pop_assignment_for_cores`) simply dequeues `para_id`s once they are "ready" (2 blocks after ordering, for async backing) with no re-validation against `paras` state: [4](#0-3) . The scheduler's coretime assigner consumes these popped `ParaId`s as `CoreAssignment::Task`/pool assignments without any `is_parathread` re-check either: [5](#0-4)  and [6](#0-5) . A repository-wide search confirms there is no `is_parathread`/`ParaLifecycle` check anywhere in the `scheduler` module that would filter such stale/invalid assignments before they reach a core.

Because a parachain's lifecycle transition to `OffboardingParathread`/removal is driven by the `ActionsQueue` at session boundaries (a window that can span many more than the 2-block async-backing delay), a `para_id` that is valid at order-placement time can become invalid before `pop_assignment_for_cores` actually schedules it, or a caller can simply supply an arbitrary/never-registered `para_id` from the start. In both cases the spot price is withdrawn/credits burned and `Revenue` is incremented for coretime that will never be productively used, since no valid candidate can ever be backed for that `para_id`.

### Impact Explanation
The orderer's own funds (balance withdrawal or on-demand credits) are irrecoverably consumed, and `Revenue::<T>` is incremented, for an order that structurally cannot result in any parachain block being produced. This breaks the accounting invariant that `Revenue` should reflect coretime that was actually usable/assignable, and violates the principle that no operation should burn user assets when it cannot execute. While the caller who places the order is also the one who loses funds (no separate victim), the loss is not always self-inflicted misuse — it can occur purely due to the protocol's own timing (order placed while `para_id` valid, then offboarded before the 2-block-later scheduling completes), which is outside the caller's control.

### Likelihood Explanation
Trivial to trigger by placing an order for a non-existent `para_id` (no on-chain existence check at all). The offboarding race is feasible but requires timing an order just before a session boundary at which a target para is offboarded (an event visible on-chain in advance via `ActionsQueue`/governance proposals), making it a realistic, low-cost, fully attacker/self-triggerable scenario, repeatable each time such offboarding occurs.

### Recommendation
Add a `paras::Pallet::<T>::is_parathread(para_id)` (or a broader "is valid on-demand parachain" check) guard in `do_place_order` before charging the sender, returning an error (e.g. a new `Error::<T>::InvalidParaId`) if the para is not a live parathread. Additionally, consider re-validating `para_id` validity in `pop_assignment_for_cores`/`advance_assignments_single_impl` before finalizing a core assignment, refunding or requeuing (without re-charging) orders whose para became invalid in the interim.

### Proof of Concept
Rust unit test in `polkadot/runtime/parachains/src/on_demand/tests.rs`:
1. Do not call `schedule_blank_para` for `para_id` (or call it and then drive the para through `OffboardingParathread` before advancing blocks) so `Paras::is_parathread(para_id) == false`.
2. Call `OnDemand::place_order_with_credits` (or `place_order_allow_death`) with sufficient balance/credits for `para_id`; assert it returns `Ok(())` (demonstrating no validity check blocks it).
3. Assert `Credits::<Test>::get(alice)` decreased by `spot_price` (or balance withdrawn) and `Revenue::<Test>::get()[0]` increased by `spot_price`.
4. Advance blocks past the 2-block async-backing delay and call `OnDemand::pop_assignment_for_cores(current_block, 1)`; assert it still yields `Some(para_id)` even though `Paras::is_parathread(para_id)` is `false`, proving the pipeline accepted and would attempt to schedule an assignment for a para that can never back a candidate, while `Revenue` accounting has already been permanently incremented with no refund path.

### Citations

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

**File:** polkadot/runtime/parachains/src/scheduler/assigner_coretime/mod.rs (L560-599)
```rust
/// Pop assignments for `now`.
fn advance_assignments_single_impl<T: Config>(
	now: BlockNumberFor<T>,
	core_states: &mut BTreeMap<CoreIndex, CoreDescriptor<BlockNumberFor<T>>>,
	mut mode: AccessMode<T>,
) -> AdvancedAssignments {
	let mut bulk_assignments = Vec::with_capacity(num_coretime_cores::<T>() as _);
	let mut pool_cores = Vec::with_capacity(num_coretime_cores::<T>() as _);
	for (core_idx, core_state) in core_states.iter_mut() {
		ensure_workload::<T>(now, *core_idx, core_state, &mode);

		let Some(work_state) = core_state.current_work.as_mut() else { continue };

		// Wrap around:
		work_state.pos = work_state.pos % work_state.assignments.len() as u16;
		let (a_type, a_state) = &mut work_state
			.assignments
			.get_mut(work_state.pos as usize)
			.expect("We limited pos to the size of the vec one line above. qed");

		// advance for next pop:
		a_state.remaining = a_state.remaining.saturating_sub(work_state.step);
		if a_state.remaining < work_state.step {
			// Assignment exhausted, need to move to the next and credit remaining for
			// next round.
			work_state.pos += 1;
			// Reset to ratio + still remaining "credits":
			a_state.remaining = a_state.remaining.saturating_add(a_state.ratio);
		}
		match *a_type {
			CoreAssignment::Pool => pool_cores.push(*core_idx),
			CoreAssignment::Task(para_id) => bulk_assignments.push((*core_idx, para_id.into())),
			CoreAssignment::Idle => {},
		}
	}

	let pool_assignments = mode.pop_assignment_for_ondemand_cores(now, pool_cores.len() as _);
	let pool_assignments = pool_cores.into_iter().zip(pool_assignments).collect();

	AdvancedAssignments { bulk_assignments, pool_assignments }
```
