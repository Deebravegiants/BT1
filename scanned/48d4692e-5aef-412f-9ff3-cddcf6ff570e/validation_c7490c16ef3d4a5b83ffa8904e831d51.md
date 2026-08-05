### Title
`schedule_para_cleanup` offboards a parathread without pruning the on-demand order queue, permanently stranding paid orders - ([File: polkadot/runtime/parachains/src/on_demand/mod.rs] + [File: polkadot/runtime/parachains/src/paras/mod.rs])

### Summary
`paras_registrar::deregister` → `paras::schedule_para_cleanup` immediately flips a parathread's `ParaLifecycle` to `OffboardingParathread`, which makes `is_valid_para` return `false` right away, while HRMP correctly tears down that para's channels at the following session boundary via `clean_hrmp_after_outgoing`. The on-demand pallet, however, has no equivalent lifecycle hook: `OrderQueue::pop_assignment_for_cores` and `advance_assignments_single_impl` pop and assign `ParaId`s purely by elapsed-block readiness, never checking `paras::Pallet::<T>::is_valid_para`. An order placed for a para that gets deregistered before the order is popped is consumed from the queue (funds/credits already withdrawn) but can never be serviced, and there is no refund or re-queue path for this case.

### Finding Description
`do_deregister` (paras_registrar) requires only `ParaLifecycle::Parathread`/`None` and calls `schedule_para_cleanup`: [1](#0-0) 

`schedule_para_cleanup` immediately transitions the lifecycle to `OffboardingParathread` (not at session boundary — that happens on the *next* action-queue apply), and only checks PVF pre-checking status and UMP queue occupancy — nothing about outstanding on-demand orders: [2](#0-1) 

`is_valid_para` treats any offboarding lifecycle as invalid immediately: [3](#0-2) 

Meanwhile, a user can place an on-demand order for *any* `para_id` (not just their own) by paying with balance or credits; funds/credits are withdrawn synchronously and the order is pushed into `OrderQueue`: [4](#0-3) 

The queue-popping logic that later hands the `ParaId` to the scheduler only checks time-readiness (`ordered_at + 2 <= now`) — it never re-validates that the para is still a live, valid parachain/parathread: [5](#0-4) 

and the scheduler's `advance_assignments_single_impl`/`pop_assignment_for_ondemand_cores` path likewise performs no `is_valid_para` check before creating a `CoreAssignment::Pool` core assignment for the popped `ParaId`: [6](#0-5) [7](#0-6) 

The only "give it another chance" path (`push_back_order`) is invoked solely when the caller-supplied `is_blocked(core_idx)` closure reports the core blocked (e.g., availability/affinity reasons) in `advance_assignments`: [8](#0-7) 

This closure has no relation to whether the assigned `ParaId` is still a registered/valid para. Once a deregistering para's validation code/head data is removed at the next session's `apply_actions_queue` (`OffboardingParathread` branch removes `Heads`, `CurrentCodeHash`, etc.), no collator can ever produce a backable candidate for that `ParaId`, so an assignment already popped for it is permanently wasted: the core sits idle for that slot, the order is gone from the queue, and neither the payer's balance withdrawal nor spent credits are refunded.

By contrast, HRMP correctly wires this lifecycle transition into its own session-boundary cleanup (`clean_hrmp_after_outgoing`, invoked from `perform_outgoing_para_cleanup`), refunding deposits for channels involving an outgoing para: [9](#0-8) [10](#0-9) 

This asymmetry confirms the on-demand pallet is missing the equivalent cleanup/refund hook that the (older, pre-on_demand-pallet) scheduler design explicitly called out as a requirement: "prune all on-demand claims corresponding to de-registered parachains" — a behavior documented in the implementers-guide but not present in the current `on_demand` pallet implementation, which has no `initializer_on_new_session` participation at all (it is explicitly "not handled by the initializer"): [11](#0-10) 

### Impact Explanation
Any unprivileged account with balance or on-demand credits can place an order for a `para_id`, and the para's manager (also unprivileged, holding no root/relay-governance rights, just ownership of their own para) can call `deregister` on that same para. The race window is trivially achievable: place the order, then call `deregister` before the order clears the 2-block async-backing readiness window (or even after, since the para lifecycle becomes `OffboardingParathread`/is fully removed at the very next session regardless of when the order was placed). The payer's withdrawn balance is moved into the on-demand pallet's pot account as "revenue" or the payer's credits are burned, yet the purchased blockspace can never be delivered and there is no mechanism to detect or refund this specific loss — the order simply vanishes from the queue once popped. This is a direct, permanent loss of user funds/credits with no compensating event or recovery path, violating the "user-controlled assets must remain fully backed" invariant.

### Likelihood Explanation
- No special privilege is required beyond being a parachain manager (a normal, permissionless registrar role) and any account with spendable balance or credits.
- The deregistration path (`Root, para owner (unlocked), or para itself`) is reachable by a signed extrinsic from the owner without any coordination with third parties.
- The race is easy to win: a malicious or careless para manager can simply deregister right after seeing/being informed an order lands in the queue for their para (order placement and the resulting queue state are public on-chain data), or can proactively deregister the para whenever any order exists, since `schedule_para_cleanup` performs no check against `on_demand`'s `OrderQueue` at all.
- Reproducible deterministically: the outcome depends purely on relative block ordering of `place_order_*` and `deregister`, both fully attacker/user-controlled extrinsics.

### Recommendation
Add a cross-pallet cleanup hook so that when a para transitions to `OffboardingParathread`/`OffboardingParachain` (either in `schedule_para_cleanup` or in `apply_actions_queue`'s offboarding branch), the `on_demand` pallet is notified to purge any queued orders referencing that `ParaId` and refund/credit the affected payers (mirroring the balance/credit accounting already withdrawn in `do_place_order`). Alternatively, add an `is_valid_para` check in `pop_assignment_for_cores`/`advance_assignments_single_impl` so orders for invalid paras are dropped with an explicit refund event rather than silently discarded, and/or make `schedule_para_cleanup` reject offboarding (similar to the existing UMP-queue-non-empty check) while there are still pending on-demand orders for that `ParaId`.

### Proof of Concept
Rust integration test (in `polkadot/runtime/parachains/src/on_demand/tests.rs` or a cross-pallet integration test crate combining `on_demand`, `paras`, and `paras_registrar`):
1. Register and onboard a parathread `para_id` (via `paras_registrar::register` + run to session where it becomes `ParaLifecycle::Parathread`).
2. `OnDemand::credit_account(payer, X)` and `OnDemand::place_order_with_credits(payer, X, para_id)`; assert `Credits::<Test>::get(payer)` decreased by `spot_price` and the order is present in `OnDemand::peek_order_queue()`.
3. Immediately call `paras_registrar::Registrar::deregister(RuntimeOrigin::signed(manager), para_id)` (or `RuntimeOrigin::root()`), then `run_to_session` to complete offboarding (`paras::Pallet::<Test>::lifecycle(para_id).is_none()`).
4. Advance blocks past the 2-block async-backing readiness window and call `OnDemand::pop_assignment_for_cores(now, 1)`.
5. Assert either:
   - the popped iterator does **not** yield `para_id` (i.e., the order was pruned) **and** `Credits::<Test>::get(payer)` was restored to its pre-order value, or
   - the popped iterator yields `para_id` and a subsequent inclusion pipeline check proves the payer is refunded when no candidate can ever be backed for it.
   Currently neither holds: the order is silently dropped from the queue with no credit/balance restoration, demonstrating the trapped-funds bug.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L660-667)
```rust
	fn do_deregister(id: ParaId) -> DispatchResult {
		match paras::Pallet::<T>::lifecycle(id) {
			// Para must be a parathread (on-demand parachain), or not exist at all.
			Some(ParaLifecycle::Parathread) | None => {},
			_ => return Err(Error::<T>::NotParathread.into()),
		}
		polkadot_runtime_parachains::schedule_para_cleanup::<T>(id)
			.map_err(|_| Error::<T>::CannotDeregister)?;
```

**File:** polkadot/runtime/parachains/src/paras/mod.rs (L2133-2155)
```rust
		let lifecycle = ParaLifecycles::<T>::get(&id);
		match lifecycle {
			// If para is not registered, nothing to do!
			None => return Ok(()),
			Some(ParaLifecycle::Parathread) => {
				ParaLifecycles::<T>::insert(&id, ParaLifecycle::OffboardingParathread);
			},
			Some(ParaLifecycle::Parachain) => {
				ParaLifecycles::<T>::insert(&id, ParaLifecycle::OffboardingParachain);
			},
			_ => return Err(Error::<T>::CannotOffboard.into()),
		}

		let scheduled_session = Self::scheduled_session();
		ActionsQueue::<T>::mutate(scheduled_session, |v| {
			if let Err(i) = v.binary_search(&id) {
				v.insert(i, id);
			}
		});

		if <T as Config>::QueueFootprinter::message_count(UmpQueueId::Para(id)) != 0 {
			return Err(Error::<T>::CannotOffboard.into());
		}
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

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L17-27)
```rust
//! The parachain on demand assignment module.
//!
//! Implements a mechanism for taking in orders for on-demand parachain (previously parathreads)
//! assignments. This module is not handled by the initializer but is instead instantiated in the
//! `construct_runtime` macro.
//!
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

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L471-557)
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

**File:** polkadot/runtime/parachains/src/scheduler/assigner_coretime/mod.rs (L385-404)
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

```

**File:** polkadot/runtime/parachains/src/scheduler/assigner_coretime/mod.rs (L560-600)
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
}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L953-975)
```rust
	/// Iterate over all paras that were noted for offboarding and remove all the data
	/// associated with them.
	fn perform_outgoing_para_cleanup(
		config: &HostConfiguration<BlockNumberFor<T>>,
		outgoing: &[ParaId],
	) -> Weight {
		let mut w = Self::clean_open_channel_requests(config, outgoing);
		for outgoing_para in outgoing {
			Self::clean_hrmp_after_outgoing(outgoing_para);

			// we need a few extra bits of data to weigh this -- all of this is read internally
			// anyways, so no overhead.
			let ingress_count =
				HrmpIngressChannelsIndex::<T>::decode_len(outgoing_para).unwrap_or_default() as u32;
			let egress_count =
				HrmpEgressChannelsIndex::<T>::decode_len(outgoing_para).unwrap_or_default() as u32;
			w = w.saturating_add(<T as Config>::WeightInfo::force_clean_hrmp(
				ingress_count,
				egress_count,
			));
		}
		w
	}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1033-1051)
```rust
	/// Remove all storage entries associated with the given para.
	fn clean_hrmp_after_outgoing(outgoing_para: &ParaId) {
		HrmpOpenChannelRequestCount::<T>::remove(outgoing_para);
		HrmpAcceptedChannelRequestCount::<T>::remove(outgoing_para);

		let ingress = HrmpIngressChannelsIndex::<T>::take(outgoing_para)
			.into_iter()
			.map(|sender| HrmpChannelId { sender, recipient: *outgoing_para });
		let egress = HrmpEgressChannelsIndex::<T>::take(outgoing_para)
			.into_iter()
			.map(|recipient| HrmpChannelId { sender: *outgoing_para, recipient });
		let mut to_close = ingress.chain(egress).collect::<Vec<_>>();
		to_close.sort();
		to_close.dedup();

		for channel in to_close {
			Self::close_hrmp_channel(&channel);
		}
	}
```
