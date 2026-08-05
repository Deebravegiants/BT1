Audit Report

## Title
`claim_revenue` allows any signed account to permanently destroy another user's pooled coretime revenue claim before settlement, returning success with a semantically incomplete/zero payout - (File: substrate/frame/broker/src/dispatchable_impls.rs)

## Summary
`claim_revenue` in `substrate/frame/broker/src/lib.rs` only calls `ensure_signed(origin)?` before invoking `Self::do_claim_revenue(region_id, max_timeslices)`, with no check that the caller owns or is the `payee` of the `region_id`'s `ContributionRecord`. [1](#0-0)  Inside `do_claim_revenue`, the loop advances `region.begin` and decrements `contribution.length` before checking whether `InstaPoolHistory::<T>::get(r)` exists, using `continue` when it does not — silently treating unsettled/future timeslices as already claimed. [2](#0-1)  Because `InstaPoolHistory` for a timeslice is only populated once `process_pool` (at commitment) and later `process_revenue` (at relay-chain revenue report) run, any signed account can call `claim_revenue` on a victim's region immediately after it is pooled — before those ticks occur — driving `contribution.length` to zero and permanently deleting the `InstaPoolContribution` record with a zero payout, while the call still returns `Ok(())` and emits `RevenueClaimPaid { amount: 0, next: None }`.

## Finding Description
The extrinsic-level check is confirmed to be `ensure_signed(origin)?` with no `payee`/ownership verification, meaning any account, not just `contribution.payee`, can invoke `claim_revenue` for any `region_id`. [3](#0-2) 

`do_claim_revenue` takes the `ContributionRecord` via `InstaPoolContribution::<T>::take(region)`, then iterates over `region.begin..last`, unconditionally advancing `region.begin` and decrementing `contribution.length` on every iteration *before* checking `InstaPoolHistory::<T>::get(r)`. If the record is absent, the loop uses `continue`, consuming that timeslice as if it had been fully accounted for: [4](#0-3) 

The `InstaPoolContribution` entry is only reinserted if `contribution.length > 0` after the loop; otherwise, it is permanently gone since it was already `take`n at the top of the function. [5](#0-4) 

`InstaPoolHistory` for timeslice `r` is only created by `process_pool`, which runs at commitment time using accumulated `InstaPoolIo`, and `maybe_payout` is only set later by `process_revenue` upon a relay-chain revenue report. [6](#0-5)  Meanwhile `do_pool` inserts `InstaPoolContribution` immediately at pooling time, independent of whether those timeslices have been committed or settled. [7](#0-6)  This creates a real time window in which a pooled region's `InstaPoolContribution` exists but its corresponding `InstaPoolHistory` records do not yet exist, during which the described "continue-through-unsettled-timeslices" bug is exploitable by anyone.

The referenced test suite corroborates the intended, correct usage pattern (advance chain time until revenue is settled via `process_revenue`, then claim), and existing tests never exercise a premature claim, confirming there is no safeguard preventing this. [8](#0-7) 

## Impact Explanation
This is a griefing/fund-destruction bug: any unprivileged signed account can call `claim_revenue` against any other user's pooled `RegionId`, immediately after observing it pooled, causing the region's `InstaPoolContribution` record to be permanently deleted with a zero payout while returning `Ok(())`/`RevenueClaimPaid{ amount: 0 }` — indistinguishable from a legitimate, fully-settled zero-revenue outcome. Since the reduction of `InstaPoolHistoryRecord::private_contributions` only happens when a settled record is actually found, the victim's share of future revenue is orphaned in the pot, matching an accounting-drift/fund-loss condition. This does not let the attacker steal funds directly (payout always goes to `contribution.payee`), but it destroys the victim's ability to ever claim the real revenue for that region, which is a legitimate impact.

## Likelihood Explanation
The exploit requires only a single unprivileged signed extrinsic call with no special timing beyond calling shortly after observing a `Pooled` event, and is repeatable against every newly pooled region. The bug is fully deterministic and directly reachable from the public dispatchable given the confirmed lack of ownership checks and the confirmed `continue`-on-missing-history behavior.

## Recommendation
1. Enforce in `claim_revenue`/`do_claim_revenue` that the caller matches `contribution.payee` (or an authorized delegate), preventing third parties from acting on another user's contribution.
2. In `do_claim_revenue`, distinguish "not yet committed/settled" from "already paid and cleaned up": when `InstaPoolHistory::<T>::get(r)` is `None` because timeslice `r` has not yet been processed (e.g., `r >= status.last_committed_timeslice`), `break` instead of `continue`, preserving `region.begin`/`contribution.length` for a future call rather than silently consuming the claim.

## Proof of Concept
As given in the report: pool a region as account 1 with `payee = 1`; immediately (before `advance_to` reaches the commit/revenue-report block) have an unrelated account 2 call `Broker::do_claim_revenue(region, 100)`. This drives `contribution.length` to 0 through the `continue` branch, deletes `InstaPoolContribution` for the region, transfers 0, and emits `RevenueClaimPaid{ amount: 0, next: None }`. Later, when real revenue is reported via `process_revenue` for those timeslices, the victim's subsequent `do_claim_revenue(region, 100)` call fails with `Error::<Test>::UnknownContribution`, and the victim's balance remains unchanged, demonstrating permanent, unrecoverable loss of the victim's pooled revenue entitlement caused by an unrelated, unprivileged third party. This can be added as an integration test in `substrate/frame/broker/src/tests.rs` following the pattern of existing tests such as `instapool_payouts_work`.

### Citations

**File:** substrate/frame/broker/src/lib.rs (L838-848)
```rust
		#[pallet::call_index(12)]
		#[pallet::weight(T::WeightInfo::claim_revenue(*max_timeslices))]
		pub fn claim_revenue(
			origin: OriginFor<T>,
			region_id: RegionId,
			max_timeslices: Timeslice,
		) -> DispatchResultWithPostInfo {
			ensure_signed(origin)?;
			Self::do_claim_revenue(region_id, max_timeslices)?;
			Ok(Pays::No.into())
		}
```

**File:** substrate/frame/broker/src/dispatchable_impls.rs (L392-417)
```rust
	pub(crate) fn do_pool(
		region_id: RegionId,
		maybe_check_owner: Option<T::AccountId>,
		payee: T::AccountId,
		finality: Finality,
	) -> Result<(), Error<T>> {
		if let Some((region_id, region)) = Self::utilize(region_id, maybe_check_owner, finality)? {
			let workplan_key = (region_id.begin, region_id.core);
			let mut workplan = Workplan::<T>::get(&workplan_key).unwrap_or_default();
			let duration = region.end.saturating_sub(region_id.begin);
			if workplan
				.try_push(ScheduleItem { mask: region_id.mask, assignment: CoreAssignment::Pool })
				.is_ok()
			{
				Workplan::<T>::insert(&workplan_key, &workplan);
				let size = region_id.mask.count_ones() as i32;
				InstaPoolIo::<T>::mutate(region_id.begin, |a| a.private.saturating_accrue(size));
				InstaPoolIo::<T>::mutate(region.end, |a| a.private.saturating_reduce(size));
				let record = ContributionRecord { length: duration, payee };
				InstaPoolContribution::<T>::insert(&region_id, record);
			}

			Self::deposit_event(Event::Pooled { region_id, duration });
		}
		Ok(())
	}
```

**File:** substrate/frame/broker/src/dispatchable_impls.rs (L419-456)
```rust
	pub(crate) fn do_claim_revenue(
		mut region: RegionId,
		max_timeslices: Timeslice,
	) -> DispatchResult {
		ensure!(max_timeslices > 0, Error::<T>::NoClaimTimeslices);
		let mut contribution =
			InstaPoolContribution::<T>::take(region).ok_or(Error::<T>::UnknownContribution)?;
		let contributed_parts = region.mask.count_ones();

		Self::deposit_event(Event::RevenueClaimBegun { region, max_timeslices });

		let mut payout = BalanceOf::<T>::zero();
		let last = region.begin + contribution.length.min(max_timeslices);
		for r in region.begin..last {
			region.begin = r + 1;
			contribution.length.saturating_dec();

			let Some(mut pool_record) = InstaPoolHistory::<T>::get(r) else { continue };
			let Some(total_payout) = pool_record.maybe_payout else { break };
			let p = total_payout
				.saturating_mul(contributed_parts.into())
				.checked_div(&pool_record.private_contributions.into())
				.unwrap_or_default();

			payout.saturating_accrue(p);
			pool_record.private_contributions.saturating_reduce(contributed_parts);

			let remaining_payout = total_payout.saturating_sub(p);
			if !remaining_payout.is_zero() && pool_record.private_contributions > 0 {
				pool_record.maybe_payout = Some(remaining_payout);
				InstaPoolHistory::<T>::insert(r, &pool_record);
			} else {
				InstaPoolHistory::<T>::remove(r);
			}
			if !p.is_zero() {
				Self::deposit_event(Event::RevenueClaimItem { when: r, amount: p });
			}
		}
```

**File:** substrate/frame/broker/src/dispatchable_impls.rs (L458-470)
```rust
		if contribution.length > 0 {
			InstaPoolContribution::<T>::insert(region, &contribution);
		}
		T::Currency::transfer(&Self::account_id(), &contribution.payee, payout, Expendable)
			.defensive_ok();
		let next = if last < region.begin + contribution.length { Some(region) } else { None };
		Self::deposit_event(Event::RevenueClaimPaid {
			who: contribution.payee,
			amount: payout,
			next,
		});
		Ok(())
	}
```

**File:** substrate/frame/broker/src/tick_impls.rs (L299-316)
```rust
	pub(crate) fn process_pool(when: Timeslice, status: &mut StatusRecord) {
		let pool_io = InstaPoolIo::<T>::take(when);
		status.private_pool_size = (status.private_pool_size as SignedCoreMaskBitCount)
			.saturating_add(pool_io.private) as CoreMaskBitCount;
		status.system_pool_size = (status.system_pool_size as SignedCoreMaskBitCount)
			.saturating_add(pool_io.system) as CoreMaskBitCount;
		let record = InstaPoolHistoryRecord {
			private_contributions: status.private_pool_size,
			system_contributions: status.system_pool_size,
			maybe_payout: None,
		};
		InstaPoolHistory::<T>::insert(when, record);
		Self::deposit_event(Event::<T>::HistoryInitialized {
			when,
			private_pool_size: status.private_pool_size,
			system_pool_size: status.system_pool_size,
		});
	}
```

**File:** substrate/frame/broker/src/tests.rs (L687-717)
```rust
#[test]
fn instapool_payouts_work() {
	TestExt::new().endow(1, 1000).execute_with(|| {
		let item = ScheduleItem { assignment: Pool, mask: CoreMask::complete() };
		assert_ok!(Broker::do_reserve(Schedule::truncate_from(vec![item])));
		assert_ok!(Broker::do_start_sales(100, 2));
		advance_to(2);
		let region = Broker::do_purchase(1, u64::max_value()).unwrap();
		assert_eq!(revenue(), 100);
		assert_ok!(Broker::do_pool(region, None, 2, Final));
		assert_ok!(Broker::do_purchase_credit(1, 20, 1));
		assert_eq!(pot(), 0);
		assert_eq!(revenue(), 100);
		advance_to(8);
		assert_ok!(TestCoretimeProvider::spend_instantaneous(1, 10));
		advance_to(11);
		// Should get revenue amount 10 from RC, from which 6 is system payout (goes to account0
		// instantly) and the rest is private (kept in the pot until claimed)
		assert_eq!(pot(), 4);
		assert_eq!(revenue(), 106);

		// Cannot claim for 0 timeslices.
		assert_noop!(Broker::do_claim_revenue(region, 0), Error::<Test>::NoClaimTimeslices);

		// Revenue can be claimed.
		assert_ok!(Broker::do_claim_revenue(region, 100));
		assert_eq!(pot(), 0);
		assert_eq!(revenue(), 106);
		assert_eq!(balance(2), 4);
	});
}
```
