Audit Report

## Title
Missing origin-privilege check in `do_reschedule`/`do_reschedule_named` allows any `ScheduleOrigin`-authorized caller to reschedule tasks owned by a higher/incomparable-privileged origin - (File: substrate/frame/scheduler/src/lib.rs)

## Summary
`do_cancel` and `do_cancel_named` call `Self::ensure_privilege(o, &s.origin)` before removing another origin's scheduled task, correctly rejecting `None`/`Ordering::Less` privilege comparisons as `BadOrigin`. `do_reschedule` and `do_reschedule_named` take no origin parameter and never call `ensure_privilege`, so they unconditionally take, re-place, and re-time any task addressed by `(when, index)` or `TaskName`, regardless of who originally scheduled it.

## Finding Description
The privilege check is defined and used asymmetrically. `ensure_privilege` rejects both a strictly-lower comparison and an incomparable comparison: [1](#0-0) 

`do_cancel` forwards the caller's origin and validates it against the stored task's origin before removing it: [2](#0-1) 

`do_cancel_named` does the same: [3](#0-2) 

In contrast, `do_reschedule` has no origin parameter at all and mutates the agenda entry unconditionally: [4](#0-3) 

And `do_reschedule_named` likewise has no origin parameter and no privilege check against `task.origin` before repositioning it: [5](#0-4) 

This confirms the code behaves exactly as described in the claim: the reschedule paths are missing the `ensure_privilege` call that exists symmetrically in the cancel paths, verified directly by reading the current `lib.rs` source.

## Impact Explanation
If `T::ScheduleOrigin` in a runtime is configured to authorize multiple distinct origin kinds (e.g., different governance tracks/collectives) that are mutually incomparable or ranked lower/higher under `T::OriginPrivilegeCmp`, any caller satisfying `ScheduleOrigin::ensure_origin` for the `reschedule`/`reschedule_named` extrinsics can move the execution block of a task scheduled by a different, higher- or incomparable-privileged origin (including Root-scheduled tasks) — without passing the privilege check that governs cancellation. This breaks the invariant, explicitly enforced for cancel, that a scheduled task can only be canceled/rescheduled by an origin at least as privileged as (or comparable to) the one that created it. The impact is a griefing/disruption vector against privileged scheduled dispatch (e.g., delaying enactment of a referendum or Root-scheduled call), not fund loss or contract insolvency directly, but a genuine violation of an intended access-control invariant in in-scope pallet code.

## Likelihood Explanation
Exploitability depends entirely on the runtime's configuration of `T::ScheduleOrigin` and `T::OriginPrivilegeCmp`. In the default/minimal configuration used by `substrate/frame/scheduler`'s own mock and many simple runtimes, `ScheduleOrigin` is `EnsureRoot`, which collapses to a single privilege level and eliminates the attack surface (only Root could call reschedule anyway). The claim itself acknowledges the precondition ("realistic configuration in production runtimes that grant scheduler access to multiple collectives/tracks") is necessary but is runtime-dependent, not a universal property of the pallet. Regardless of that dependency, the code-level asymmetry between cancel and reschedule is real and reachable whenever a runtime configures `ScheduleOrigin` to admit more than one non-comparable/ranked origin, which is a legitimate and common pattern (e.g., OpenGov tracks). The finding is a genuine logic bug in the shared scheduler pallet.

## Recommendation
Thread the caller's `PalletsOrigin` into `do_reschedule` and `do_reschedule_named`, mirroring `do_cancel`/`do_cancel_named`, and call `Self::ensure_privilege(o, &task.origin)` before taking/re-placing the task, so `None`/`Ordering::Less` comparisons are rejected symmetrically with the cancellation paths. Update the `reschedule`/`reschedule_named` dispatchables to pass `origin.caller()` through accordingly.

## Proof of Concept
Add a test in `substrate/frame/scheduler/src/tests.rs` analogous to the existing `should_use_origin` cancel tests: schedule a named task under `root()` via `do_schedule_named`, then call the public `reschedule_named` extrinsic from an account/origin that satisfies `T::ScheduleOrigin` but has lower/incomparable rank under a custom `OriginPrivilegeCmp` (as used in the pallet's privilege-comparison test scaffolding). Currently this call succeeds and moves the task's execution time; after applying the fix (threading origin + `ensure_privilege`), the same call should return `BadOrigin`, matching the symmetric behavior already verified for `cancel_named`.

### Citations

**File:** substrate/frame/scheduler/src/lib.rs (L1078-1088)
```rust
		let scheduled = Agenda::<T>::try_mutate(when, |agenda| {
			agenda.get_mut(index as usize).map_or(
				Ok(None),
				|s| -> Result<Option<Scheduled<_, _, _, _, _>>, DispatchError> {
					if let (Some(ref o), Some(ref s)) = (origin, s.borrow()) {
						Self::ensure_privilege(o, &s.origin)?;
					};
					Ok(s.take())
				},
			)
		})?;
```

**File:** substrate/frame/scheduler/src/lib.rs (L1103-1122)
```rust
	fn do_reschedule(
		(when, index): TaskAddress<BlockNumberFor<T>>,
		new_time: DispatchTime<BlockNumberFor<T>>,
	) -> Result<TaskAddress<BlockNumberFor<T>>, DispatchError> {
		let new_time = Self::resolve_time(new_time)?;

		if new_time == when {
			return Err(Error::<T>::RescheduleNoChange.into());
		}

		let task = Agenda::<T>::try_mutate(when, |agenda| {
			let task = agenda.get_mut(index as usize).ok_or(Error::<T>::NotFound)?;
			ensure!(!matches!(task, Some(Scheduled { maybe_id: Some(_), .. })), Error::<T>::Named);
			task.take().ok_or(Error::<T>::NotFound)
		})?;
		Self::cleanup_agenda(when);
		Self::deposit_event(Event::Canceled { when, index });

		Self::place_task(new_time, task).map_err(|x| x.0)
	}
```

**File:** substrate/frame/scheduler/src/lib.rs (L1165-1187)
```rust
	fn do_cancel_named(origin: Option<T::PalletsOrigin>, id: TaskName) -> DispatchResult {
		Lookup::<T>::try_mutate_exists(id, |lookup| -> DispatchResult {
			if let Some((when, index)) = lookup.take() {
				let i = index as usize;
				Agenda::<T>::try_mutate(when, |agenda| -> DispatchResult {
					if let Some(s) = agenda.get_mut(i) {
						if let (Some(ref o), Some(ref s)) = (origin, s.borrow()) {
							Self::ensure_privilege(o, &s.origin)?;
							Retries::<T>::remove((when, index));
							T::Preimages::drop(&s.call);
						}
						*s = None;
					}
					Ok(())
				})?;
				Self::cleanup_agenda(when);
				Self::deposit_event(Event::Canceled { when, index });
				Ok(())
			} else {
				return Err(Error::<T>::NotFound.into());
			}
		})
	}
```

**File:** substrate/frame/scheduler/src/lib.rs (L1189-1209)
```rust
	fn do_reschedule_named(
		id: TaskName,
		new_time: DispatchTime<BlockNumberFor<T>>,
	) -> Result<TaskAddress<BlockNumberFor<T>>, DispatchError> {
		let new_time = Self::resolve_time(new_time)?;

		let lookup = Lookup::<T>::get(id);
		let (when, index) = lookup.ok_or(Error::<T>::NotFound)?;

		if new_time == when {
			return Err(Error::<T>::RescheduleNoChange.into());
		}

		let task = Agenda::<T>::try_mutate(when, |agenda| {
			let task = agenda.get_mut(index as usize).ok_or(Error::<T>::NotFound)?;
			task.take().ok_or(Error::<T>::NotFound)
		})?;
		Self::cleanup_agenda(when);
		Self::deposit_event(Event::Canceled { when, index });
		Self::place_task(new_time, task).map_err(|x| x.0)
	}
```

**File:** substrate/frame/scheduler/src/lib.rs (L1529-1538)
```rust
	fn ensure_privilege(
		left: &<T as Config>::PalletsOrigin,
		right: &<T as Config>::PalletsOrigin,
	) -> Result<(), DispatchError> {
		if matches!(T::OriginPrivilegeCmp::cmp_privilege(left, right), Some(Ordering::Less) | None)
		{
			return Err(BadOrigin.into());
		}
		Ok(())
	}
```
