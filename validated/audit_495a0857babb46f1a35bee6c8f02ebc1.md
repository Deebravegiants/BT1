### Title
Missing origin-privilege check in `do_reschedule_named` allows any `ScheduleOrigin`-authorized caller to reschedule tasks owned by a higher/incomparable-privileged origin - (File: substrate/frame/scheduler/src/lib.rs)

### Summary
`do_cancel`/`do_cancel_named` correctly call `Self::ensure_privilege(o, &s.origin)` before mutating another origin's scheduled task, and `ensure_privilege` rejects both `Some(Ordering::Less)` and `None` (incomparable) as `BadOrigin`. `do_reschedule` and `do_reschedule_named`, however, take no origin argument at all and never call `ensure_privilege`, so any caller who merely satisfies the generic `T::ScheduleOrigin::ensure_origin` check in the dispatchable can reschedule (delay/move) a task that was originally scheduled by a strictly higher-privileged or an incomparable-privileged origin.

### Finding Description
`ensure_privilege` treats both a strictly-lower comparison and an incomparable (`None`) comparison as `BadOrigin`: [1](#0-0) 

This check is correctly invoked in the cancellation paths: [2](#0-1) [3](#0-2) 

But `do_reschedule_named` (and `do_reschedule`) never accept or check the origin of the requester against the stored task's origin at all — the function signature and body contain no `ensure_privilege` call, no origin parameter, and no comparison against `scheduled.origin`: [4](#0-3) [5](#0-4) 

The dispatchable calling `do_reschedule_named` (the `reschedule_named` extrinsic, wired through `T::ScheduleOrigin::ensure_origin`) only proves the caller is *some* origin authorized to use the scheduler pallet at all — it does not prove the caller has privilege comparable to or higher than the origin that originally created task `id`. This is asymmetric with the cancellation path, which explicitly forwards `origin.caller()` into `ensure_privilege` for exactly this purpose. As a result, if `T::ScheduleOrigin` is configured (as is typical in real runtimes, e.g. an `EitherOf`/`EnsureOneOf` covering multiple tracks/collectives) to admit multiple origin kinds that are mutually incomparable or of lower rank under `T::OriginPrivilegeCmp`, any of those origins can call `reschedule_named`/`reschedule` on a `TaskName` scheduled by a different, higher- or incomparable-privileged origin (including Root-scheduled tasks), and move its execution time arbitrarily (e.g., far into the future), with no origin-ownership check at all.

### Impact Explanation
A lower- or incomparable-privileged, but scheduler-authorized, origin can silently delay/derail execution of another origin's scheduled privileged call (e.g., a governance-enacted referendum, treasury payout, or Root-scheduled runtime action) by rescheduling it to a much later block, without ever needing to pass `ensure_privilege`. This is a concrete disruption of privileged scheduled dispatch — the invariant that "an origin cannot cancel/reschedule a task belonging to a strictly higher or incomparable-privileged origin" is violated for the reschedule path (it holds only for cancel).

### Likelihood Explanation
Requires two distinct origins both satisfying `T::ScheduleOrigin` with incomparable/unequal privilege under `T::OriginPrivilegeCmp` — a realistic configuration in production runtimes that grant scheduler access to multiple collectives/tracks. The attacker only needs to know the `TaskName` (often a well-known/derivable identifier for governance-related scheduled calls) and call the public `reschedule_named` extrinsic; no storage or governance access is needed beyond normal `ScheduleOrigin` authorization.

### Recommendation
Thread the caller's `PalletsOrigin` into `do_reschedule`/`do_reschedule_named` (as already done for `do_cancel`/`do_cancel_named`) and call `Self::ensure_privilege(o, &task.origin)` before allowing the reschedule to proceed, so that `None`/`Ordering::Less` comparisons are rejected symmetrically with the cancellation paths.

### Proof of Concept
```rust
// substrate/frame/scheduler/src/tests.rs (new test)
#[test]
fn reschedule_named_bypasses_privilege_check() {
    new_test_ext().execute_with(|| {
        let call = RuntimeCall::Logger(LoggerCall::log { i: 42, weight: Weight::from_parts(10, 0) });
        // Root schedules a named task.
        Scheduler::do_schedule_named(
            [1u8; 32], DispatchTime::At(4), None, 127, root(),
            Preimage::bound(call).unwrap(),
        ).unwrap();

        // A lower-privileged/incomparable origin (e.g. signed(1)) invokes the
        // public `reschedule_named` extrinsic, which only checks T::ScheduleOrigin,
        // not ownership/privilege of task [1u8;32].
        assert_ok!(Scheduler::reschedule_named(
            signed_origin_allowed_by_schedule_origin(1),
            [1u8; 32],
            DispatchTime::At(100),
        ));
        // EXPECTED (fix): should return BadOrigin, mirroring do_cancel_named's
        // symmetric rejection when OriginPrivilegeCmp::cmp_privilege returns
        // None/Less for the two origins.
    });
}
```
Expected assertion after fix: `assert_noop!(Scheduler::reschedule_named(...), BadOrigin)`, matching the existing `should_use_origin`-style symmetry tests for `cancel_named`.

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
