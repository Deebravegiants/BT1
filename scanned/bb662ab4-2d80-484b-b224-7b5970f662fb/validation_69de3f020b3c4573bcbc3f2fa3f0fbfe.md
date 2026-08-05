### Title
`pool` extrinsic can silently drop the region while returning success when the per-core `Workplan` is full - (File: substrate/frame/broker/src/dispatchable_impls.rs, function `do_pool`)

### Summary
`do_pool` calls `Self::utilize()` which unconditionally consumes the region (removing it from `Regions` and only reinstating it for `Finality::Provisional`), and only *conditionally* records the pool bookkeeping (`Workplan`, `InstaPoolIo`, `InstaPoolContribution`) behind an `if workplan.try_push(...).is_ok()` guard. If the push fails (bounded `Workplan` for that `(begin, core)` key is already full), the function still returns `Ok(())` and unconditionally emits `Event::Pooled`, even though no pooling bookkeeping was created and (for `Finality::Final`) the region itself was permanently destroyed.

### Finding Description
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
``` [1](#0-0) 

`utilize` always removes the region from `Regions`, and only reinserts it if `finality == Finality::Provisional`:
```rust
Regions::<T>::remove(&region_id);
...
if finality == Finality::Provisional {
    Regions::<T>::insert(&region_id, &region);
}
Ok(Some((region_id, region)))
``` [2](#0-1) 

`Workplan` entries per `(begin, core)` are a bounded vector (`Schedule`, bounded by a max-items constant). An attacker who owns a core can use `interlace`/`assign`/`pool` on many small mask fragments of the same `(begin, core)` slot to fill that `Workplan` entry to its bound. Once full, any further `pool(region_id, payee, Final)` call on a remaining/overlapping fragment of that same `(begin, core)` will:
1. Pass `utilize()` successfully, permanently removing the region (`Regions::remove`) since finality is `Final` (no reinsertion path).
2. Fail the `workplan.try_push(...)` silently — no error is surfaced, so `InstaPoolContribution`, `InstaPoolIo`, and `Workplan` are never updated for this region.
3. Still emit `Event::Pooled { region_id, duration }` and return `DispatchResultWithPostInfo::Ok`.

The extrinsic wrapper compounds this:
```rust
pub fn pool(
    origin: OriginFor<T>,
    region_id: RegionId,
    payee: T::AccountId,
    finality: Finality,
) -> DispatchResultWithPostInfo {
    let who = ensure_signed(origin)?;
    Self::do_pool(region_id, Some(who), payee, finality)?;
    Ok(if finality == Finality::Final { Pays::No } else { Pays::Yes }.into())
}
``` [3](#0-2) 
With `Finality::Final`, the call is even fee-free (`Pays::No`), so the attacker pays nothing while the region's coretime rights vanish with no InstaPool credit ever recorded for the `payee`, and no way for any downstream public call (`claim_revenue`, `purchase`, `assign`, `partition`, `interlace`) to recover or reconcile the lost region — it's simply gone from `Regions` and never entered the pool schedule.

The core issue: `Event::Pooled` and the overall `Ok(())` result are not gated on whether the `Workplan::try_push` actually succeeded, so the pallet reports "success" for a state transition that is only half-applied (region consumed, bookkeeping missing).

### Impact Explanation
A signed, unprivileged account can cause coretime regions (a saleable/valuable resource) to be irrecoverably destroyed while the chain state and emitted events claim the pooling succeeded. For `Finality::Final` this is a real, uncompensated, fee-free loss of the region with no InstaPool credit created for the `payee` — effectively the coretime "evaporates" instead of being pooled or refunded, and any consumer relying on `Event::Pooled` or on `InstaPoolContribution`/`Workplan` state to reconcile revenue will see an inconsistent terminal state (event says pooled, storage says otherwise). This matches "pool insolvency" / broken accounting rather than a shallow success check.

### Likelihood Explanation
Reaching the bound requires filling `Workplan` for a specific `(begin, core)` slot with enough `ScheduleItem`s (via `interlace`/`assign`/`pool` on core-mask fragments) to hit the bounded vector's max length — feasible for any account that owns (or has purchased) that core, since `interlace` and `assign`/`pool` are all plain signed-origin calls with no privileged requirement. The exact bound (`MaxItemsPerCore`-style constant) determines the number of fragment operations needed, but it is a fixed, attacker-reachable constant, not requiring any race condition — fully deterministic and repeatable in a single block/test.

### Recommendation
- Make `do_pool` propagate a hard error (e.g. `Error::<T>::TooManyWorkplanItems`) when `workplan.try_push` fails instead of silently skipping bookkeeping.
- Only emit `Event::Pooled` inside the successful branch, not unconditionally after the `if`.
- Ensure that on `try_push` failure the region is not lost: either abort before `utilize()`'s irreversible `Regions::remove` (check workplan capacity first), or reinsert/refund the region for `Finality::Final` as well when pooling cannot be completed.

### Proof of Concept
Rust integration test (in `substrate/frame/broker/src/tests.rs` style):
1. `do_start_sales`, `do_purchase` a core to get `region_id` covering full `CoreMask::complete()`.
2. Repeatedly `do_interlace` the region into many small disjoint mask fragments and `do_assign(..., Final)` each fragment to a task, filling `Workplan::get((begin, core))` up to its bounded capacity (`MaxItemsPerCore`-equivalent constant used in `Schedule`'s `BoundedVec`).
3. Take one remaining unassigned fragment `region_x` and call `Broker::pool(signed(owner), region_x, payee, Finality::Final)`.
4. Assert:
   - Call returns `Ok(_)` and `Event::Pooled { region_id: region_x, .. }` is emitted.
   - `Regions::<Test>::get(&region_x)` is `None` (region destroyed).
   - `InstaPoolContribution::<Test>::get(&region_x)` is `None` (no bookkeeping created).
   - `Workplan::<Test>::get((region_x.begin, region_x.core))` unchanged / does not contain the `Pool` assignment for `region_x`'s mask.
   - Subsequent `Broker::do_claim_revenue(region_x, ...)` returns `Error::<Test>::UnknownContribution`, confirming the region's coretime is unrecoverable despite the earlier "success" event.

### Citations

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

**File:** substrate/frame/broker/src/utility_impls.rs (L119-138)
```rust
		Regions::<T>::remove(&region_id);

		let last_committed_timeslice = status.last_committed_timeslice;
		if region_id.begin <= last_committed_timeslice {
			let duration = region.end.saturating_sub(region_id.begin);
			region_id.begin = last_committed_timeslice + 1;
			if region_id.begin >= region.end {
				Self::deposit_event(Event::RegionDropped { region_id, duration });
				return Ok(None);
			}
		} else {
			Workplan::<T>::mutate_extant((region_id.begin, region_id.core), |p| {
				p.retain(|i| (i.mask & region_id.mask).is_void())
			});
		}
		if finality == Finality::Provisional {
			Regions::<T>::insert(&region_id, &region);
		}

		Ok(Some((region_id, region)))
```

**File:** substrate/frame/broker/src/lib.rs (L819-828)
```rust
		pub fn pool(
			origin: OriginFor<T>,
			region_id: RegionId,
			payee: T::AccountId,
			finality: Finality,
		) -> DispatchResultWithPostInfo {
			let who = ensure_signed(origin)?;
			Self::do_pool(region_id, Some(who), payee, finality)?;
			Ok(if finality == Finality::Final { Pays::No } else { Pays::Yes }.into())
		}
```
