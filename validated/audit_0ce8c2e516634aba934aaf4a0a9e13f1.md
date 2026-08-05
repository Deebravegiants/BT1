This confirms `do_place_order` performs no validation on `para_id` against `paras::Pallet` lifecycle state before charging the sender and enqueuing the order.

Audit Report

## Title
Missing `para_id` validity check in `do_place_order` allows credit-burning and potential permanent `OrderQueue` exhaustion (`Error::QueueFull` DoS) - (File: polkadot/runtime/parachains/src/on_demand/mod.rs)

## Summary
`Pallet::do_place_order` never validates that `para_id` is a registered/onboarded parathread before charging the caller (via `Currency::withdraw` or `Credits::<T>` decrement) and pushing the order into the queue. [1](#0-0)  This allows any signed account to place orders for a bogus, never-onboarded `para_id`, burning credits/balance, corrupting `Revenue::<T>` accounting, and potentially exhausting the order queue.

## Finding Description
`do_place_order` only checks spot price against `max_amount` and queue length against `on_demand_queue_max_size` before debiting the sender and pushing `para_id` unconditionally into `order_status.queue`. [2](#0-1)  There is no call to `paras::Pallet::<T>::is_parathread`, `is_parachain`, or any lifecycle check on `para_id` anywhere in `mod.rs` — the only occurrences of `is_parathread` in the on_demand module are in the test file, not production code. Revenue accounting via `Revenue::<T>::mutate` proceeds identically regardless of whether `para_id` is valid. [3](#0-2)  `pop_assignment_for_cores` and `push_back_order` are generic queue operations with no para validity awareness, consistent with the claim.

## Impact Explanation
The primary concrete impact is self-inflicted: an attacker burns their own `Credits::<T>`/balance on orders for a para that can never consume coretime, and pollutes `Revenue::<T>` with amounts attributed to an invalid `para_id`. This is a real accounting-integrity bug but has limited direct value to an attacker since they lose their own funds. The claimed "permanent queue exhaustion" DoS is speculative — it depends on unverified assumptions about how `pop_assignment_for_cores`/`push_back_order` are invoked by the scheduler/assignment-provider integration layer (not shown in this file) and whether invalid-para orders are actually re-queued rather than dropped. The report itself acknowledges this is conditional ("If the assignment provider re-queues..."). Without confirmation of that downstream behavior, the DoS claim is not proven, only the credit-burning/accounting-corruption issue is demonstrated by the code shown.

## Likelihood Explanation
The precondition (funded/credited account) is trivial and the call path (`place_order_with_credits`/`place_order_allow_death`/`place_order_keep_alive` with an unregistered `para_id`) is fully reachable by any unprivileged signed account, matching the claim.

## Recommendation
Add a validity check in `do_place_order`, e.g. `ensure!(paras::Pallet::<T>::is_parathread(para_id), Error::<T>::InvalidParaId);`, before charging the sender and pushing to the queue. Additionally verify/ensure the scheduler/assignment-provider layer drops (rather than requeues) orders whose `para_id` is no longer valid at assignment time.

## Proof of Concept
Extend `polkadot/runtime/parachains/src/on_demand/tests.rs`: credit an attacker account, call `place_order_with_credits` repeatedly with a `para_id` never passed through `schedule_blank_para` (unregistered), and observe that each call succeeds, `Credits::<T>` decreases, and `Revenue::<T>` increases despite `para_id` being invalid — confirming the credit-burn/accounting-corruption path. Full confirmation of the queue-exhaustion DoS would additionally require tracing the scheduler/assignment-provider's actual handling of popped assignments for invalid paras (whether they call `push_back_order` or drop the order), which was not verified in this review.

### Citations

**File:** polkadot/runtime/parachains/src/on_demand/mod.rs (L471-548)
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
```
